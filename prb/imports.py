"""Checking that imports point to something that exists.

Ruff does not do it, while PyCharm underlines these mistakes in red.
The student's folder plays the role of the project root, as during the exam.
"""

import ast
import importlib
import importlib.util
import sys

from prb.sources import Problem, SourceFile

# Standard modules that can be imported without any side effect.
_SAFE_MODULES = {
    "abc", "array", "bisect", "calendar", "cmath", "collections", "collections.abc", "copy",
    "csv", "dataclasses", "datetime", "decimal", "enum", "fractions", "functools", "heapq",
    "io", "itertools", "json", "math", "operator", "os", "os.path", "pathlib", "pickle",
    "pprint", "random", "re", "secrets", "statistics", "string", "sys", "textwrap", "time",
    "types", "typing", "unicodedata", "uuid",
}  # fmt: skip
_MODULE_ATTRIBUTES = {"__name__", "__file__", "__doc__", "__all__", "__path__", "__dict__"}


def check_imports(sources: dict[str, SourceFile]) -> list[Problem]:
    """Find imports of unknown modules and unknown names of known modules.

    :param sources: the student's files, indexed by path
    :return: one problem per broken import or attribute
    """
    project = _Project(sources)
    problems = []
    for source in sources.values():
        if source.tree is not None:
            problems.extend(_check_file(source, project))
    return problems


class _Project:
    """What can be imported from the student's folder."""

    def __init__(self, sources: dict[str, SourceFile]) -> None:
        self.modules = {source.module: source for source in sources.values() if source.module}
        self.packages = set()
        for name in sources:
            parts = name.split("/")[:-1]
            self.packages.update(".".join(parts[: i + 1]) for i in range(len(parts)))

    def exists(self, module: str) -> bool:
        return module in self.modules or module in self.packages

    def names(self, module: str) -> set[str] | None:
        """Names that a module offers, or None when they cannot be listed."""
        children = {
            other[len(module) + 1 :].split(".")[0]
            for other in self.modules.keys() | self.packages
            if other.startswith(module + ".")
        }
        source = self.modules.get(module)
        if source is None:
            return children | _MODULE_ATTRIBUTES
        if source.tree is None:
            return None
        defined = top_level_names(source.tree)
        return None if defined is None else defined | children | _MODULE_ATTRIBUTES

    def where_is(self, short_name: str) -> str | None:
        """Dotted name of a module placed somewhere else in the project."""
        for module in sorted(self.modules):
            if module.rsplit(".", 1)[-1] == short_name and module != short_name:
                return module
        return None


def top_level_names(tree: ast.Module) -> set[str] | None:
    """List the names defined by a module.

    :param tree: the parsed module
    :return: the names, or None if a star import makes the list unknowable
    """
    names: set[str] = set()
    for node in _walk_scope(tree.body):
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


def _walk_scope(body: list[ast.stmt]):
    """Walk statements without entering functions and classes."""
    pending: list[ast.AST] = list(body)
    while pending:
        node = pending.pop()
        yield node
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            pending.extend(ast.iter_child_nodes(node))


def _check_file(source: SourceFile, project: _Project) -> list[Problem]:
    problems: list[Problem] = []
    bound: dict[str, str] = {}

    def report(node: ast.AST, message: str) -> None:
        problems.append(Problem(message, source.name, node.lineno, source.line(node.lineno)))

    for node in ast.walk(source.tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                message = _check_module(alias.name, project)
                if message:
                    report(node, message)
                elif alias.asname:
                    bound[alias.asname] = alias.name
                else:
                    top = alias.name.split(".")[0]
                    bound[top] = top
        elif isinstance(node, ast.ImportFrom):
            module = _absolute_module(node, source)
            message = (
                "import relatif impossible ici : écris le nom complet du module"
                if module is None
                else _check_module(module, project)
            )
            if message:
                report(node, message)
                continue
            for alias in node.names:
                message = _check_name(module, alias.name, project)
                if message:
                    report(node, message)
                elif project.exists(f"{module}.{alias.name}"):
                    bound[alias.asname or alias.name] = f"{module}.{alias.name}"
    _forget_rebound_names(source.tree, bound)
    _check_attributes(source.tree, bound, project, report)
    return problems


def _absolute_module(node: ast.ImportFrom, source: SourceFile) -> str | None:
    if node.level == 0:
        return node.module
    package = source.module.split(".") if source.is_package else source.module.split(".")[:-1]
    drop = node.level - 1
    if drop >= len(package):
        return None
    base = package[: len(package) - drop]
    return ".".join(base + ([node.module] if node.module else []))


def _check_module(module: str, project: _Project) -> str | None:
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


def _check_name(module: str, name: str, project: _Project) -> str | None:
    if name == "*":
        return None
    if project.exists(module):
        names = project.names(module)
        if names is not None and name not in names:
            return f"« {name} » n'existe pas dans le module « {module} »"
    elif module in _SAFE_MODULES:
        found = hasattr(importlib.import_module(module), name) or _stdlib_exists(f"{module}.{name}")
        if not found:
            return f"« {name} » n'existe pas dans le module « {module} »"
    return None


def _forget_rebound_names(tree: ast.Module, bound: dict[str, str]) -> None:
    """Ignore imported names that are also used as variables or parameters."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            bound.pop(node.id, None)
        elif isinstance(node, ast.arg):
            bound.pop(node.arg, None)


def _check_attributes(tree: ast.Module, bound: dict[str, str], project: _Project, report) -> None:
    """Check ``module.name`` expressions on imported modules."""
    seen = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute) or not isinstance(node.ctx, ast.Load):
            continue
        parts = _dotted_parts(node)
        if parts is None or parts[0] not in bound:
            continue
        module = bound[parts[0]]
        for name in parts[1:]:
            message = _check_name(module, name, project)
            if message and (node.lineno, message) not in seen:
                seen.add((node.lineno, message))
                report(node, message)
            if message or not project.exists(f"{module}.{name}"):
                break
            module = f"{module}.{name}"


def _dotted_parts(node: ast.expr) -> list[str] | None:
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        return None
    parts.append(node.id)
    return parts[::-1]
