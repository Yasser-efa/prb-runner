"""Checking of the bank itself (command ``valider``).

Messages never contain a hidden test, a hint or a piece of a solution, since the person who
runs the command is also the one who trains with the exercises.
"""

import os
import re
import shutil
import tempfile
from collections.abc import Iterator, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field, replace
from pathlib import Path

from prb.bank import load_exercise, load_order
from prb.literals import LiteralError, parse_call, parse_literal
from prb.model import BankError, Case, Exercise
from prb.paths import Paths
from prb.sources import list_files
from prb.verdict import Verdict, judge, run_reference, verify

MIN_HIDDEN_CASES = 6
HINT_COUNTS = (2, 3)
SPEED_MARGIN = 2
_EXAMPLE = re.compile(r"^>>> (?P<call>.+)\n(?P<result>(?:(?!>>>|```).*\n)*)", re.MULTILINE)


@dataclass
class Validation:
    """Result of the checking of one exercise."""

    exercise_id: str
    problems: list[str] = field(default_factory=list)
    visible: int = 0
    hidden: int = 0
    hints: int = 0


def validate_bank(paths: Paths, wanted: Sequence[str] = ()) -> Iterator[Validation]:
    """Check some exercises, several at a time.

    :param paths: the project folders
    :param wanted: identifiers to check, all of them if empty
    :return: the results, in the order of the bank
    """
    names = list(wanted) or load_order(paths)
    with ThreadPoolExecutor(max_workers=min(4, os.cpu_count() or 1)) as pool:
        yield from pool.map(lambda name: validate_exercise(paths, name), names)


def check_order(paths: Paths) -> list[str]:
    """Compare ``ordre.toml`` with the folders.

    :param paths: the project folders
    :return: the problems
    """
    order = set(load_order(paths))
    public = {path.parent.name for path in paths.exercises.glob("*/exercice.toml")}
    private = {path.name for path in paths.private.iterdir() if path.is_dir()}
    problems = [f"{name} n'est pas dans ordre.toml" for name in sorted(public - order)]
    problems += [f"{name} n'a pas d'exercice.toml" for name in sorted(order - public)]
    problems += [f"_prive/{name} ne correspond à rien" for name in sorted(private - public)]
    return problems


def validate_exercise(paths: Paths, exercise_id: str) -> Validation:
    """Check that an exercise is complete, consistent and feasible.

    :param paths: the project folders
    :param exercise_id: the exercise
    :return: the result
    """
    result = Validation(exercise_id)
    try:
        exercise = load_exercise(paths, exercise_id)
        result.hints = len(exercise.hints)
        with tempfile.TemporaryDirectory(prefix="prb_", ignore_cleanup_errors=True) as name:
            verdict = verify(exercise, assemble(exercise, Path(name) / exercise.id))
    except BankError as error:
        result.problems.append(str(error))
        return result
    result.visible, result.hidden = len(exercise.visible_cases), len(exercise.hidden_cases)
    result.problems += _check_verdict(verdict)
    result.problems += _check_content(exercise)
    result.problems += _check_statement(exercise)
    if not result.problems:
        result.problems += _check_examples(exercise)
        result.problems += _check_speed(exercise)
    return result


def assemble(exercise: Exercise, folder: Path) -> Path:
    """Copy the reference solution and the provided files, as a student would submit them.

    :param exercise: the exercise
    :param folder: the folder to create
    :return: the same folder
    """
    shutil.copytree(exercise.reference_folder, folder)
    for file in exercise.provided:
        target = folder / file.name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(file.read())
    return folder


def _check_verdict(verdict: Verdict) -> Iterator[str]:
    for problem in verdict.admissibility:
        yield f"solution non recevable : {problem.message}"
    for problem in verdict.warnings:
        yield f"avertissement sur la solution : {problem.message}"
    for problem in verdict.constraints:
        yield f"contrainte non respectée par la solution : {problem.message}"
    for problem in verdict.absent:
        yield f"solution incomplète : {problem.message}"
    failed = sum(not report.ok for report in verdict.visible)
    if failed:
        yield f"la solution rate {failed} test(s) visible(s)"
    if not all(report.ok for report in verdict.hidden):
        yield "la solution ne donne pas toujours le même résultat"
    for remark in verdict.remarks:
        yield f"qualité de la solution : {remark.message}"


def _check_content(exercise: Exercise) -> Iterator[str]:
    if len(exercise.hidden_cases) < MIN_HIDDEN_CASES:
        yield f"moins de {MIN_HIDDEN_CASES} tests cachés"
    if len(exercise.hints) not in HINT_COUNTS:
        yield "il faut 2 ou 3 indices"
    for kind, cases in (("visible", exercise.visible_cases), ("caché", exercise.hidden_cases)):
        for function in exercise.functions:
            # A function without parameters has only one possible call.
            untestable = kind == "caché" and not function.parameters
            if not untestable and not any(case.function is function for case in cases):
                yield f"aucun test {kind} pour {function.name}"
        if exercise.kind == "programme" and not any(case.is_program for case in cases):
            yield f"aucun test {kind} pour le programme"
    extra = set(list_files(exercise.reference_folder)) - set(exercise.files)
    if extra:
        yield f"fichiers en trop dans la solution : {', '.join(sorted(extra))}"
    known = {_key(case) for case in exercise.visible_cases}
    hidden = [_key(case) for case in exercise.hidden_cases]
    duplicates = [key for key in hidden if key in known]
    if duplicates:
        yield f"{len(duplicates)} test(s) caché(s) identique(s) à un test visible"
    if len(set(hidden)) != len(hidden):
        yield "tests cachés en double"


def _key(case: Case) -> tuple:
    """Identify what a case does."""
    name = case.function.name if case.function else None
    return name, repr(case.args), repr(case.kwargs), case.stdin, case.seed


def _check_statement(exercise: Exercise) -> Iterator[str]:
    """Check that the statement announces everything that is verified."""
    files = [*exercise.files, *(file.name for file in exercise.provided)]
    python = [name for name in files if name.endswith(".py") and "__init__" not in name]
    expected = [name.rsplit("/", 1)[-1] for name in python]
    expected += [part for name in files for part in name.split("/")[:-1]]
    expected += [function.name for function in exercise.functions]
    for constraint in exercise.constraints:
        expected += constraint.forbidden + constraint.required
        expected += constraint.forbidden_functions + constraint.forbidden_modules
        expected += constraint.required_calls
        expected += [f"`{module}`" for module in constraint.required_modules]
    for text in dict.fromkeys(expected):
        if text not in exercise.statement:
            yield f"l'énoncé ne mentionne pas « {text} »"
    for function in exercise.functions:
        if function.preserve_arguments and "modifi" not in exercise.statement:
            yield "l'énoncé ne dit pas que les arguments ne doivent pas être modifiés"


def statement_examples(exercise: Exercise) -> list[Case]:
    """Read the ``>>>`` examples of a statement.

    The text under a call is the returned value or, if it is not a Python value, what the
    function displays.

    :param exercise: the exercise
    :return: the examples that call a function of the exercise
    """
    functions = {function.name: function for function in exercise.functions}
    cases = []
    for match in _EXAMPLE.finditer(exercise.statement):
        try:
            call = parse_call(match["call"])
        except LiteralError:
            continue
        if call.function not in functions:
            continue
        case = Case(
            label=call.source,
            function=functions[call.function],
            args=call.args,
            kwargs=tuple(call.kwargs.items()),
        )
        text = match["result"].rstrip("\n")
        try:
            cases.append(replace(case, has_value=True, value=parse_literal(text)))
        except LiteralError:
            cases.append(replace(case, output=text))
    return cases


def _check_examples(exercise: Exercise) -> Iterator[str]:
    cases = statement_examples(exercise)
    report = run_reference(exercise, cases, exercise.timeout)
    for result in judge(cases, report.outcomes):
        if not result.ok:
            yield f"exemple faux dans l'énoncé : {result.case.label}"
    if not exercise.main and not cases:
        yield "l'énoncé ne contient aucun exemple"


def _check_speed(exercise: Exercise) -> Iterator[str]:
    """Check that the solution is far from the time limit."""
    cases = [*exercise.visible_cases, *exercise.hidden_cases]
    limit = exercise.timeout / SPEED_MARGIN
    report = run_reference(exercise, cases, limit)
    if any(outcome.status == "timeout" for outcome in report.outcomes):
        yield f"la solution met plus de {limit:g} s sur un test"
