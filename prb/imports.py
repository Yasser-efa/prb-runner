"""Checking that imports point to something that exists.

Ruff does not do it. The severities follow the inspections of PyCharm 2026.2: an import that
cannot be resolved is an error (red icon), while a missing attribute of a module or an import
that depends on the launched file is only a warning. The student's folder plays the role of the
project root, as during the exam.
"""

import ast
import importlib
import importlib.util
import sys
from collections.abc import Iterator
from dataclasses import dataclass, field

from prb.sources import Problem, SourceFile, is_main_guard

# Standard modules that can be imported without any side effect.
_SAFE_MODULES = {
    "abc", "array", "bisect", "calendar", "cmath", "collections", "collections.abc", "copy",
    "csv", "dataclasses", "datetime", "decimal", "enum", "fractions", "functools", "heapq",
    "io", "itertools", "json", "math", "operator", "os", "os.path", "pathlib", "pickle",
    "pprint", "random", "re", "secrets", "statistics", "string", "sys", "textwrap", "time",
    "types", "typing", "unicodedata", "uuid",
}  # fmt: skip
_MODULE_ATTRIBUTES = {
    "__name__", "__file__", "__doc__", "__all__", "__path__", "__dict__", "__init__",
}  # fmt: skip


@dataclass
class ImportReport:
    """What is wrong with the imports: errors are red in PyCharm, warnings are not."""

    errors: list[Problem] = field(default_factory=list)
    warnings: list[Problem] = field(default_factory=list)


def check_imports(sources: dict[str, SourceFile]) -> ImportReport:
    """Find imports of unknown modules and unknown names of known modules.

    :param sources: the student's files, indexed by path
    :return: the broken imports and attributes
    """
    project = Project(sources)
    report = ImportReport()
    for source in sources.values():
        if source.tree is not None:
            _FileChecker(source, project, report).check()
    return report


def star_names(source: SourceFile, project: Project) -> set[str] | None:
    """List the names brought by the star imports of a file.

    :param source: a file with a correct syntax
    :param project: what can be imported
    :return: the names, or None if they cannot be listed
    """
    names: set[str] = set()
    for node in ast.walk(source.tree):
        if isinstance(node, ast.ImportFrom) and any(alias.name == "*" for alias in node.names):
            found = project.public_names(_absolute_module(node, source))
            if found is None:
                return None
            names |= found
    return names


class Project:
    """What can be imported from the student's folder."""

    def __init__(self, sources: dict[str, SourceFile]) -> None:
        self.modules = {source.module: source for source in sources.values() if source.module}
        self.packages = set()
        for name in sources:
            parts = name.split("/")[:-1]
            self.packages.update(".".join(parts[: i + 1]) for i in range(len(parts)))

    def exists(self, module: str) -> bool:
        """Tell whether a module or a package is in the project."""
        return module in self.modules or module in self.packages

    def names(self, module: str) -> set[str] | None:
        """Names that a module offers, or None when they cannot be listed."""
        children = {
            other[len(module) + 1 :].split(".")[0]
            for other in self.modules.keys() | self.packages
            if other.startswith(f"{module}.")
        }
        source = self.modules.get(module)
        if source is None:
            return children | _MODULE_ATTRIBUTES
        if source.tree is None:
            return None
        defined = top_level_names(source.tree)
        return None if defined is None else defined | children | _MODULE_ATTRIBUTES

    def public_names(self, module: str | None) -> set[str] | None:
        """Names given by ``from module import *``, or None when they cannot be listed."""
        names: set[str] | None = None
        if module in self.modules:
            tree = self.modules[module].tree
            names = tree and top_level_names(tree)
        elif module in self.packages:
            names = set()
        elif module in _SAFE_MODULES:
            content = importlib.import_module(module)
            names = set(getattr(content, "__all__", dir(content)))
        return names and {name for name in names if not name.startswith("_")}

    def where_is(self, short_name: str) -> str | None:
        """Dotted name of a module placed somewhere else in the project."""
        for module in sorted(self.modules):
            if module.rsplit(".", 1)[-1] == short_name and module != short_name:
                return module
        return None


def top_level_names(tree: ast.Module) -> set[str] | None:
    """List the names that a module gives to those who import it.

    :param tree: the parsed module
    :return: the names, or None if a star import makes the list unknowable
    """
    names: set[str] = set()
    for node in _walk_scope([node for node in tree.body if not is_main_guard(node)]):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            names.add(node.id)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                if alias.name == "*":
                    return None
                names.add(alias.asname or alias.name.split(".")[0])
    return names


def _walk_scope(body: list[ast.stmt]) -> Iterator[ast.AST]:
    """Walk statements without entering functions and classes."""
    pending: list[ast.AST] = list(body)
    while pending:
        node = pending.pop()
        yield node
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            pending.extend(ast.iter_child_nodes(node))


class _FileChecker:
    """Checks the imports of one file."""

    def __init__(self, source: SourceFile, project: Project, report: ImportReport) -> None:
        self.source = source
        self.project = project
        self.report = report
        self.bound: dict[str, str] = {}

    def check(self) -> None:
        guarded = _guarded_imports(self.source.tree)
        for node in ast.walk(self.source.tree):
            if id(node) in guarded:
                continue
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self._check_import(node, alias)
            elif isinstance(node, ast.ImportFrom):
                self._check_from(node)
        _forget_rebound_names(self.source.tree, self.bound)
        self._check_attributes()

    def _error(self, node: ast.AST, message: str) -> None:
        self.report.errors.append(self._problem(node, message))

    def _warning(self, node: ast.AST, message: str) -> None:
        problem = self._problem(node, message)
        if problem not in self.report.warnings:
            self.report.warnings.append(problem)

    def _problem(self, node: ast.AST, message: str) -> Problem:
        line = node.lineno
        return Problem(message, self.source.name, line, self.source.line(line))

    def _check_import(self, node: ast.Import, alias: ast.alias) -> None:
        module = self._resolve(node, alias.name)
        if module is None:
            return
        if alias.asname:
            self.bound[alias.asname] = module
        elif module == alias.name:
            top = alias.name.split(".")[0]
            self.bound[top] = top

    def _check_from(self, node: ast.ImportFrom) -> None:
        if node.level == 0:
            module = self._resolve(node, node.module)
        else:
            module = self._resolve_relative(node)
        if module is None:
            return
        for alias in node.names:
            message = _missing_name(module, alias.name, self.project)
            if message:
                self._error(node, message)
            elif self.project.exists(_join(module, alias.name)):
                self.bound[alias.asname or alias.name] = _join(module, alias.name)

    def _resolve(self, node: ast.AST, module: str) -> str | None:
        """Find the real name of an imported module, and report it if it does not exist."""
        message = _missing_module(module, self.project)
        if message is None:
            return module
        # PyCharm also looks next to the importing file, unlike Python launched from main.py.
        folder = self.source.name.rpartition("/")[0].replace("/", ".")
        sibling = _join(folder, module)
        if folder and self.project.exists(sibling):
            self._warning(
                node,
                f"« {module} » n'est trouvé que si on lance ce fichier : "
                f"depuis main.py, écris « {sibling} »",
            )
            return sibling
        self._error(node, message)
        return None

    def _resolve_relative(self, node: ast.ImportFrom) -> str | None:
        module = _absolute_module(node, self.source)
        if module is None:
            self._error(node, "import relatif impossible : il sort du projet")
            return None
        if self.source.name.count("/") == node.level - 1:
            self._warning(
                node, "import relatif à la racine, refusé par Python : écris le nom du module"
            )
        if module:
            message = _missing_module(module, self.project)
            if message:
                self._error(node, message)
                return None
        return module

    def _check_attributes(self) -> None:
        """Check ``module.name`` expressions on imported modules."""
        for node in ast.walk(self.source.tree):
            if not isinstance(node, ast.Attribute) or not isinstance(node.ctx, ast.Load):
                continue
            parts = _dotted_parts(node)
            if parts is None or parts[0] not in self.bound:
                continue
            module = self.bound[parts[0]]
            for name in parts[1:]:
                message = _missing_name(module, name, self.project)
                if message:
                    self._warning(node, message)
                if message or not self.project.exists(_join(module, name)):
                    break
                module = _join(module, name)


def _join(module: str, name: str) -> str:
    return f"{module}.{name}" if module else name


def _guarded_imports(tree: ast.Module) -> set[int]:
    """Identify the imports inside a ``try``, whose failure may be expected."""
    guarded = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Try) and node.handlers:
            for statement in node.body:
                guarded.update(id(child) for child in ast.walk(statement))
    return guarded


def _absolute_module(node: ast.ImportFrom, source: SourceFile) -> str | None:
    """Give the full name of the module of a ``from`` import.

    :return: the name, empty for the project root, None outside the project
    """
    if node.level == 0:
        return node.module
    folder = source.name.split("/")[:-1]
    drop = node.level - 1
    if drop > len(folder):
        return None
    base = folder[: len(folder) - drop]
    return ".".join(base + ([node.module] if node.module else []))


def _missing_module(module: str, project: Project) -> str | None:
    top = module.split(".")[0]
    if project.exists(top):
        if project.exists(module):
            return None
        return f"le module « {module} » n'existe pas dans ton projet"
    if top in sys.stdlib_module_names:
        return None if _stdlib_exists(module) else f"le module « {module} » n'existe pas"
    elsewhere = project.where_is(top)
    if elsewhere:
        return f"module « {module} » introuvable : depuis la racine, il s'appelle « {elsewhere} »"
    return (
        f"module « {module} » introuvable : ni un fichier de ton projet, "
        "ni la bibliothèque standard"
    )


def _stdlib_exists(module: str) -> bool:
    try:
        return importlib.util.find_spec(module) is not None
    except (ImportError, ValueError, AttributeError):
        return False


def _missing_name(module: str, name: str, project: Project) -> str | None:
    if name == "*":
        return None
    place = f"le module « {module} »" if module else "la racine du projet"
    if not module or project.exists(module):
        names = project.names(module) if module else _root_names(project)
        if names is not None and name not in names:
            return f"« {name} » n'existe pas dans {place}"
    elif module in _SAFE_MODULES:
        found = hasattr(importlib.import_module(module), name) or _stdlib_exists(f"{module}.{name}")
        if not found:
            return f"« {name} » n'existe pas dans {place}"
    return None


def _root_names(project: Project) -> set[str]:
    return {module.split(".")[0] for module in project.modules.keys() | project.packages}


def _forget_rebound_names(tree: ast.Module, bound: dict[str, str]) -> None:
    """Ignore imported names that are also used as variables or parameters."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            bound.pop(node.id, None)
        elif isinstance(node, ast.arg):
            bound.pop(node.arg, None)


def _dotted_parts(node: ast.expr) -> list[str] | None:
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        return None
    parts.append(node.id)
    return parts[::-1]
