"""The four steps of the verdict, in the order of the exam."""

from collections.abc import Sequence
from dataclasses import dataclass, field, replace
from enum import Enum
from pathlib import Path

from prb.admissibility import check_admissibility
from prb.bank import BankError, Case, Exercise
from prb.comparison import same_output, same_value, type_difference
from prb.constraints import check_constraints
from prb.quality import IMPORTS, PRACTICE, check_quality, sort_remarks
from prb.runner import Outcome, run_cases
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


@dataclass
class Verdict:
    """Complete result of a verification."""

    exercise: Exercise
    admissibility: list[Problem] = field(default_factory=list)
    constraints: list[Problem] = field(default_factory=list)
    visible: list[CaseReport] = field(default_factory=list)
    hidden: list[CaseReport] = field(default_factory=list)
    remarks: list[Problem] = field(default_factory=list)

    @property
    def status(self) -> Status:
        """Result of the first step that failed."""
        if self.admissibility:
            return Status.NOT_ADMISSIBLE
        if self.constraints:
            return Status.CONSTRAINTS
        if all(report.ok for report in [*self.visible, *self.hidden]):
            return Status.PASSED
        return Status.FAILED

    @property
    def passed(self) -> bool:
        """Tell whether the exercise is done."""
        return self.status is Status.PASSED


def verify(exercise: Exercise, folder: Path) -> Verdict:
    """Check some code against an exercise.

    The check stops at the first blocking step that fails, as a rejected submission is not
    evaluated at the exam.

    :param exercise: the exercise
    :param folder: the folder holding the code
    :return: the verdict
    """
    verdict = Verdict(exercise)
    sources = read_sources(folder)
    verdict.admissibility = check_admissibility(exercise, folder, sources)
    if verdict.admissibility:
        return verdict
    verdict.constraints = check_constraints(exercise, sources)
    if not verdict.constraints:
        noisy = _run_tests(exercise, folder, verdict)
        verdict.remarks += _test_remarks(verdict, noisy)
    verdict.remarks = sort_remarks(verdict.remarks + check_quality(exercise, folder, sources))
    return verdict


def expected_hidden_cases(exercise: Exercise) -> list[Case]:
    """Complete the hidden cases with the results of the reference solution.

    :param exercise: the exercise
    :return: the hidden cases with their expected value or output
    :raises BankError: if the reference solution cannot answer a case
    """
    if not exercise.hidden_cases:
        return []
    report = run_cases(
        exercise.reference_folder, exercise.hidden_cases, exercise.main, exercise.timeout
    )
    completed = []
    for case, outcome in zip(exercise.hidden_cases, report.outcomes, strict=True):
        if outcome.status != "value" or not (case.is_program or outcome.plain):
            raise BankError(
                f"{exercise.id} : la solution de référence échoue sur un test caché "
                "(lance « python -m prb valider »)"
            )
        shows = case.is_program or bool(outcome.output)
        completed.append(
            replace(
                case,
                has_value=not case.is_program,
                value=outcome.value,
                output=outcome.output if shows else None,
            )
        )
    return completed


def judge(cases: Sequence[Case], outcomes: Sequence[Outcome]) -> list[CaseReport]:
    """Compare what happened with what was expected.

    :param cases: the cases, with their expected value or output
    :param outcomes: what happened for each case
    :return: one report per case
    """
    return [
        CaseReport(case, outcome, _is_ok(case, outcome))
        for case, outcome in zip(cases, outcomes, strict=True)
    ]


def _run_tests(exercise: Exercise, folder: Path, verdict: Verdict) -> list[str]:
    hidden = expected_hidden_cases(exercise)
    cases = [*exercise.visible_cases, *hidden]
    report = run_cases(folder, cases, exercise.main, exercise.timeout)
    judged = judge(cases, report.outcomes)
    count = len(exercise.visible_cases)
    verdict.visible, verdict.hidden = judged[:count], judged[count:]
    return report.noisy_modules


def _is_ok(case: Case, outcome: Outcome) -> bool:
    if outcome.status != "value" or outcome.modified:
        return False
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
        if report.case.has_value and not function.returns_float:
            difference = type_difference(report.case.value, outcome.value)
            message = difference and f"{report.case.label} {difference}"
        if message is None and report.case.output is None and outcome.output:
            message = f"{function.name} affiche du texte au lieu de seulement renvoyer une valeur"
        if message:
            seen.add(function.name)
            remarks.append(Problem(message, function.file, group=PRACTICE))
    return remarks
