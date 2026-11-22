"""Step 1 of the verdict: would the submission be accepted at all?

The official criteria are: every requested file is present (possibly empty), the layout of the
statement is respected, PyCharm shows no error (red icon) and a paper preparation is handed in.
The last one cannot be checked here.
"""

import ast
import difflib
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from prb.hashing import check_hashing
from prb.imports import Project, check_imports, star_names
from prb.linting import BLOCKING_RULES, STAR_RULE, UNDEFINED_RULE, LintMessage, lint
from prb.model import Exercise
from prb.patterns import check_patterns
from prb.sources import Problem, SourceFile, list_files


@dataclass
class Admissibility:
    """What makes a submission worth zero, and what could be held against it."""

    errors: list[Problem] = field(default_factory=list)
    warnings: list[Problem] = field(default_factory=list)


def check_admissibility(
    exercise: Exercise, folder: Path, sources: dict[str, SourceFile]
) -> Admissibility:
    """Apply the official criteria to a submission.

    :param exercise: the exercise
    :param folder: the student's folder
    :param sources: the Python files of that folder
    :return: the blocking problems and the warnings
    """
    red = red_errors(folder, sources)
    return Admissibility(
        errors=_check_layout(exercise, folder) + _check_provided(exercise, folder) + red.errors,
        warnings=_unexpected_files(exercise, folder) + red.warnings,
    )


def red_errors(folder: Path, sources: dict[str, SourceFile]) -> Admissibility:
    """Find what PyCharm shows with its red icon, and related warnings.

    :param folder: the student's folder
    :param sources: the Python files of that folder
    :return: the errors and the warnings
    """
    result = Admissibility()
    result.errors += [source.error for source in sources.values() if source.error]
    for problem, is_red in _check_names(folder, sources):
        (result.errors if is_red else result.warnings).append(problem)
    for source in sources.values():
        if source.tree is not None:
            result.errors += check_hashing(source)
            result.errors += check_patterns(source)
    imports = check_imports(sources)
    result.errors += imports.errors
    result.warnings += imports.warnings
    return result


def _unexpected_files(exercise: Exercise, folder: Path) -> list[Problem]:
    """Find Python files that the statement does not mention."""
    expected = {name.casefold() for name in (*exercise.files, *exercise.provided_names)}
    return [
        Problem("fichier non prévu par l'énoncé : retire-le avant de créer le ZIP", name)
        for name in list_files(folder)
        if name.endswith(".py") and name.casefold() not in expected
    ]


def _check_layout(exercise: Exercise, folder: Path) -> list[Problem]:
    present = [name for name in list_files(folder) if name not in exercise.provided_names]
    if not present:
        return [Problem(f"le dossier mes_solutions/{exercise.id}/ est vide")]
    problems = []
    for name in exercise.files:
        if name not in present:
            problems.append(Problem(_describe_missing(name, present, exercise.files)))
    return problems


def _check_provided(exercise: Exercise, folder: Path) -> list[Problem]:
    """Check that the provided files are there, and intact when they must be."""
    present = set(list_files(folder))
    problems = []
    for file in exercise.provided:
        if file.name not in present:
            message = "fichier fourni manquant : relance du_jour pour le recopier"
            problems.append(Problem(message, file.name))
        elif not file.editable and not file.matches((folder / file.name).read_bytes()):
            message = "fichier fourni modifié : c'est interdit (supprime-le et relance du_jour)"
            problems.append(Problem(message, file.name))
    return problems


def _describe_missing(name: str, present: list[str], expected: tuple[str, ...]) -> str:
    spare = [other for other in present if other not in expected]
    for other in spare:
        if other.casefold() == name.casefold():
            return f"« {other} » trouvé, mais l'énoncé demande « {name} » (majuscules comprises)"
    path = PurePosixPath(name)
    if path.name == "__init__.py":
        return f"il manque {name} : « {path.parent} » doit être un package"
    for other in spare:
        if PurePosixPath(other).name.casefold() == path.name.casefold():
            return f"« {other} » est mal placé : l'énoncé demande « {name} »"
    close = difflib.get_close_matches(name, spare, n=1, cutoff=0.75)
    suffix = f" (tu as « {close[0]} »)" if close else ""
    return f"fichier manquant : {name}{suffix}"


def _check_names(folder: Path, sources: dict[str, SourceFile]) -> Iterator[tuple[Problem, bool]]:
    """Find undefined names and misplaced statements, red in PyCharm or not."""
    files = [name for name, source in sources.items() if source.tree is not None]
    project = Project(sources)
    for message in lint(folder, files, (*BLOCKING_RULES, STAR_RULE)):
        source = sources[message.file]
        text, is_red = message.message, True
        if message.code == STAR_RULE:
            if _comes_from_star(message, source, project):
                continue
            text = f"nom « {message.name} » non défini"
        elif message.code == UNDEFINED_RULE and _is_bound_before(message, source):
            text = f"« {message.name} » peut ne pas être défini à cet endroit"
            is_red = False
        elif message.code == UNDEFINED_RULE and _is_only_quoted(message, source):
            is_red = False
        yield Problem(text, source.name, message.line, source.line(message.line)), is_red


def _comes_from_star(message: LintMessage, source: SourceFile, project: Project) -> bool:
    names = star_names(source, project)
    return names is None or message.name in names


def _is_only_quoted(message: LintMessage, source: SourceFile) -> bool:
    """Tell whether a name only appears in annotations written between quotes."""
    nodes = ast.walk(source.tree)
    return not any(isinstance(node, ast.Name) and node.id == message.name for node in nodes)


def _is_bound_before(message: LintMessage, source: SourceFile) -> bool:
    """Tell whether a name received a value earlier in the same scope.

    PyCharm only warns about such a name (deleted, or bound by a past ``except``).
    """
    scope = _scope_at(source.tree, message.line)
    return any(
        name == message.name and line < message.line for name, line in _bindings(scope)
    )


def _scope_at(tree: ast.Module, line: int) -> ast.AST:
    """Find the innermost function that contains a line."""
    scope: ast.AST = tree
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.lineno <= line <= node.end_lineno:
                scope = node
    return scope


def _bindings(scope: ast.AST) -> Iterator[tuple[str, int]]:
    """List the names bound in a scope, comprehensions and inner functions excluded."""
    pending = list(ast.iter_child_nodes(scope))
    while pending:
        node = pending.pop()
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            yield node.id, node.lineno
        elif isinstance(node, ast.ExceptHandler) and node.name:
            yield node.name, node.lineno
        if not isinstance(
            node,
            (
                ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda,
                ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp,
            ),
        ):  # fmt: skip
            pending.extend(ast.iter_child_nodes(node))
