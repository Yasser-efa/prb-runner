"""Step 4 of the verdict: what costs points without blocking the submission."""

import ast
from collections.abc import Iterator
from pathlib import Path

from prb import docstrings, loops
from prb.admissibility import unexpected_files
from prb.bank import Exercise
from prb.linting import IGNORED_RULES, QUALITY_RULES, lint
from prb.sources import Problem, SourceFile

PEP8 = "PEP 8"
NAMING = "Nommage"
DOCUMENTATION = docstrings.GROUP
IMPORTS = "Imports et organisation"
PRACTICE = loops.GROUP
GROUPS = (PEP8, NAMING, DOCUMENTATION, IMPORTS, PRACTICE)

_IMPORT_RULES = {"E401", "E402", "F401", "F403", "F405", "A004"}
_FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)


def check_quality(
    exercise: Exercise, folder: Path, sources: dict[str, SourceFile]
) -> list[Problem]:
    """List the remarks on the style of the code.

    :param exercise: the exercise
    :param folder: the student's folder
    :param sources: the student's files, all with a correct syntax
    :return: the remarks, sorted by group
    """
    remarks = [
        Problem(message.message, message.file, message.line, group=_group(message.code))
        for message in lint(folder, list(sources), QUALITY_RULES, IGNORED_RULES)
        if not message.is_syntax
    ]
    for source in sources.values():
        remarks += _check_short_names(source)
        remarks += docstrings.check_docstrings(source)
        remarks += loops.check_loop_variables(source)
    if exercise.main:
        remarks += _check_main_guard(sources[exercise.main])
    remarks += [
        Problem(problem.message, problem.file, group=IMPORTS)
        for problem in unexpected_files(exercise, folder)
    ]
    return sort_remarks(remarks)


def sort_remarks(remarks: list[Problem]) -> list[Problem]:
    """Sort remarks by group, then by file and line.

    :param remarks: the remarks in any order
    :return: the sorted remarks
    """
    return sorted(
        remarks,
        key=lambda item: (GROUPS.index(item.group), item.file or "", item.line or 0, item.message),
    )


def _group(code: str) -> str:
    if code in _IMPORT_RULES:
        return IMPORTS
    if code.startswith("N"):
        return NAMING
    if code.startswith(("F", "A")):
        return PRACTICE
    return PEP8


def _check_short_names(source: SourceFile) -> Iterator[Problem]:
    """Report names of one letter, once per function."""
    seen = set()
    for scope, name, node in _stored_names(source.tree, None):
        if len(name) == 1 and name != "_" and (scope, name) not in seen:
            seen.add((scope, name))
            place = f" dans {scope}" if scope else ""
            yield Problem(
                f"nom d'une seule lettre « {name} »{place}",
                source.name,
                node.lineno,
                group=NAMING,
            )


def _stored_names(node: ast.AST, scope: str | None) -> Iterator[tuple[str | None, str, ast.AST]]:
    """List the names created by some code, with the function that creates them."""
    for child in ast.iter_child_nodes(node):
        inner = scope
        if isinstance(child, _FUNCTIONS):
            yield scope, child.name, child
            inner = child.name
        elif isinstance(child, ast.ClassDef):
            yield scope, child.name, child
        elif isinstance(child, ast.arg):
            yield scope, child.arg, child
        elif isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store):
            yield scope, child.id, child
        elif isinstance(child, ast.ExceptHandler) and child.name:
            yield scope, child.name, child
        elif isinstance(child, (ast.MatchAs, ast.MatchStar)) and child.name:
            yield scope, child.name, child
        elif isinstance(child, (ast.Import, ast.ImportFrom)):
            for alias in child.names:
                if alias.asname:
                    yield scope, alias.asname, child
        yield from _stored_names(child, inner)


def _check_main_guard(source: SourceFile) -> Iterator[Problem]:
    for node in source.tree.body:
        if isinstance(node, ast.If) and _is_main_test(node.test):
            return
    yield Problem("il manque « if __name__ == '__main__': »", source.name, group=PRACTICE)


def _is_main_test(test: ast.expr) -> bool:
    if not (isinstance(test, ast.Compare) and len(test.ops) == 1):
        return False
    if not isinstance(test.ops[0], ast.Eq):
        return False
    sides = {ast.unparse(test.left), ast.unparse(test.comparators[0])}
    return sides == {"__name__", "'__main__'"}
