"""The four steps of the verdict, in the order of the exam."""

from collections.abc import Sequence
from dataclasses import dataclass, field, replace
from enum import Enum
from pathlib import Path

from prb.admissibility import check_admissibility
from prb.comparison import same_output, same_value, type_difference
from prb.constraints import check_constraints
from prb.controls import apply_control
from prb.model import BankError, Case, Exercise
from prb.quality import IMPORTS, PRACTICE, check_quality, sort_remarks
from prb.runner import Outcome, RunError, RunReport, run_cases
from prb.signatures import check_functions
from prb.sources import Problem, read_sources


class Status(Enum):
    """Overall result of a verification."""

    NOT_ADMISSIBLE = "non recevable"
    CONSTRAINTS = "contrainte non respectée"
    FAILED = "tests ratés"
    PASSED = "réussi"


@dataclass(frozen=True)
class CaseReport:
    """A case, what was expected and what happened."""

    case: Case
    outcome: Outcome
    ok: bool
    observed: object = None


@dataclass
class Verdict:
    """Complete result of a verification."""

    exercise: Exercise
    admissibility: list[Problem] = field(default_factory=list)
    warnings: list[Problem] = field(default_factory=list)
    constraints: list[Problem] = field(default_factory=list)
    absent: list[Problem] = field(default_factory=list)
    visible: list[CaseReport] = field(default_factory=list)
    hidden: list[CaseReport] = field(default_factory=list)
    remarks: list[Problem] = field(default_factory=list)

    @property
    def tests_passed(self) -> bool:
        """Tell whether every test succeeded."""
        return all(report.ok for report in [*self.visible, *self.hidden])

    @property
    def status(self) -> Status:
        """Result of the first step that failed."""
        if self.admissibility:
            return Status.NOT_ADMISSIBLE
        if self.constraints:
            return Status.CONSTRAINTS
        return Status.PASSED if self.tests_passed else Status.FAILED

    @property
    def passed(self) -> bool:
        """Tell whether the exercise is done."""
        return self.status is Status.PASSED


def verify(exercise: Exercise, folder: Path) -> Verdict:
    """Check some code against an exercise.

    The check stops there if the submission is not admissible, since it would not be evaluated
    at the exam. A broken constraint or a missing function does not prevent the other tests from
    running.

    :param exercise: the exercise
    :param folder: the folder holding the code
    :return: the verdict
    """
    verdict = Verdict(exercise)
    sources = read_sources(folder)
    admissibility = check_admissibility(exercise, folder, sources)
    verdict.admissibility, verdict.warnings = admissibility.errors, admissibility.warnings
    if verdict.admissibility:
        return verdict
    own = {name: file for name, file in sources.items() if name not in exercise.provided_names}
    verdict.constraints = check_constraints(exercise, own)
    noisy = _run_tests(exercise, folder, verdict, check_functions(exercise, own))
    remarks = _test_remarks(verdict, noisy) + check_quality(exercise, folder, own)
    verdict.remarks = sort_remarks(remarks)
    return verdict


def expected_hidden_cases(exercise: Exercise) -> list[Case]:
    """Complete the hidden cases with the results of the reference solution.

    :param exercise: the exercise
    :return: the hidden cases with their expected value or output
    :raises BankError: if the reference solution cannot answer a case
    """
    if not exercise.hidden_cases:
        return []
    report = run_reference(exercise, exercise.hidden_cases, exercise.timeout)
    return [
        _complete(exercise, case, outcome)
        for case, outcome in zip(exercise.hidden_cases, report.outcomes, strict=True)
    ]


def run_reference(exercise: Exercise, cases: Sequence[Case], timeout: float) -> RunReport:
    """Run some cases on the reference solution, completed with the provided files.

    :param exercise: the exercise
    :param cases: the cases to run
    :param timeout: maximum duration of one case, in seconds
    :return: the outcomes
    """
    files = {file.name: file.read() for file in exercise.provided} | exercise.test_files()
    return run_cases(exercise.reference_folder, cases, exercise.main, timeout, files)


def _complete(exercise: Exercise, case: Case, outcome: Outcome) -> Case:
    """Add to a hidden case what the reference solution gives."""
    usable = case.is_program or outcome.plain or case.control is not None
    if outcome.status != "value" or not usable:
        raise BankError(
            f"{exercise.id} : la solution de référence échoue sur un test caché "
            "(lance « python -m prb valider »)"
        )
    if case.control is not None:
        return replace(case, has_value=True, value=apply_control(case, outcome))
    shows = case.compare_output and (case.is_program or bool(outcome.output))
    return replace(
        case,
        has_value=not case.is_program,
        value=outcome.value,
        output=outcome.output if shows else None,
    )


def judge(cases: Sequence[Case], outcomes: Sequence[Outcome]) -> list[CaseReport]:
    """Compare what happened with what was expected.

    :param cases: the cases, with their expected value or output
    :param outcomes: what happened for each case
    :return: one report per case
    """
    reports = []
    for case, outcome in zip(cases, outcomes, strict=True):
        observed = outcome.value
        if case.control is not None and outcome.status == "value":
            observed = apply_control(case, outcome)
        reports.append(CaseReport(case, outcome, _is_ok(case, outcome, observed), observed))
    return reports


def _run_tests(
    exercise: Exercise, folder: Path, verdict: Verdict, absent: dict[str, Problem]
) -> list[str]:
    """Run the tests of what exists. The functions that are absent fail theirs."""
    verdict.absent = list(absent.values())
    cases = [*exercise.visible_cases, *expected_hidden_cases(exercise)]
    runnable = [case for case in cases if case.target not in absent]
    report = run_cases(folder, runnable, exercise.main, exercise.timeout, exercise.test_files())
    outcomes = iter(report.outcomes)
    judged = judge(
        cases,
        [
            Outcome("absent", error=RunError("Absente", absent[case.target].message))
            if case.target in absent
            else next(outcomes)
            for case in cases
        ],
    )
    count = len(exercise.visible_cases)
    verdict.visible, verdict.hidden = judged[:count], judged[count:]
    return report.noisy_modules


def _is_ok(case: Case, outcome: Outcome, observed: object) -> bool:
    if outcome.status != "value" or outcome.modified:
        return False
    if case.control is not None:
        return same_value(case.value, observed)
    if case.has_value and not (outcome.plain and same_value(case.value, outcome.value)):
        return False
    return case.output is None or same_output(case.output, outcome.output)


def _test_remarks(verdict: Verdict, noisy_modules: list[str]) -> list[Problem]:
    remarks = [
        Problem(
            f"le module {module} affiche du texte quand on l'importe : "
            "place ce code sous « if __name__ == '__main__': »",
            module.replace(".", "/") + ".py",
            group=IMPORTS,
        )
        for module in noisy_modules
    ]
    seen = set()
    for report in verdict.visible:
        function, outcome = report.case.function, report.outcome
        if function is None or not report.ok or function.name in seen:
            continue
        message = None
        controlled = report.case.control is not None
        if report.case.has_value and not function.returns_float and not controlled:
            difference = type_difference(report.case.value, outcome.value)
            message = difference and f"{report.case.label} {difference}"
        silent = report.case.output is None and not report.case.stdin and not controlled
        if message is None and silent and outcome.output:
            message = f"{function.name} affiche du texte au lieu de seulement renvoyer une valeur"
        if message:
            seen.add(function.name)
            remarks.append(Problem(message, function.file, group=PRACTICE))
    return remarks
