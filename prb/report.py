"""Display of verdicts in the terminal."""

from collections import Counter

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from prb.comparison import normalize_output
from prb.model import Case
from prb.quality import GROUPS
from prb.runner import Outcome, RunError
from prb.sources import Problem
from prb.verdict import CaseReport, Status, Verdict

MAX_SHOWN = 1200
_OK, _KO = Text("✓", style="bold green"), Text("✗", style="bold red")
_PANELS = {
    Status.PASSED: ("RÉUSSI", "green"),
    Status.FAILED: ("TESTS RATÉS", "red"),
    Status.CONSTRAINTS: ("CONTRAINTE NON RESPECTÉE", "red"),
    Status.NOT_ADMISSIBLE: ("NON RECEVABLE : 0 à l'examen", "red"),
}


def show_verdict(console: Console, verdict: Verdict, footer: str = "") -> None:
    """Display a complete verdict.

    :param console: the terminal
    :param verdict: the verdict
    :param footer: last line of the final panel (elapsed time, number of attempts)
    """
    exercise = verdict.exercise
    console.print()
    console.rule(Text(f"{exercise.title} ({exercise.reference})", style="bold"))
    _show_step(console, 1, "Recevabilité", verdict.admissibility)
    if verdict.status is not Status.NOT_ADMISSIBLE:
        _show_step(console, 2, "Contraintes", verdict.constraints)
    if verdict.visible:
        _show_tests(console, verdict)
    if verdict.status is not Status.NOT_ADMISSIBLE:
        _show_quality(console, verdict.remarks)
    title, color = _PANELS[verdict.status]
    body = Text(title, style=f"bold {color}", justify="center")
    if footer:
        body = Group(body, Text(footer, justify="center"))
    console.print()
    console.print(Panel(body, border_style=color))


def _title(number: int, name: str, mark: Text | None, detail: str = "") -> Text:
    text = Text.assemble("\n", (f"{number}. {name} ", "bold"))
    if mark is not None:
        text.append(mark)
    if detail:
        text.append(f"  {detail}")
    return text


def _show_step(console: Console, number: int, name: str, problems: list[Problem]) -> None:
    console.print(_title(number, name, _KO if problems else _OK))
    for problem in problems:
        console.print(_bullet(problem, "red"))


def _bullet(problem: Problem, color: str) -> Text:
    text = Text.assemble(("   • ", color), problem.message)
    if problem.location:
        text.append(f"  [{problem.location}]", style="cyan")
    if problem.source:
        text.append(f"\n       {problem.source}", style="dim")
    return text


def _show_tests(console: Console, verdict: Verdict) -> None:
    visible, hidden = verdict.visible, verdict.hidden
    done = sum(report.ok for report in visible)
    mark = _OK if all(report.ok for report in [*visible, *hidden]) else _KO
    console.print(_title(3, "Tests", mark, f"visibles : {done}/{len(visible)}"))
    table = Table(show_lines=True, expand=False)
    for column in ("Appel", "Attendu", "Obtenu"):
        table.add_column(column, overflow="fold")
    table.add_column("", justify="center")
    for report in visible:
        table.add_row(
            _describe_case(report.case),
            _describe_expected(report.case),
            _describe_outcome(report),
            _OK if report.ok else _KO,
        )
    console.print(table)
    if hidden:
        _show_hidden(console, hidden)


def _show_hidden(console: Console, hidden: list[CaseReport]) -> None:
    done = sum(report.ok for report in hidden)
    console.print(Text.assemble("   Tests cachés : ", (f"{done}/{len(hidden)}", "bold")))
    failed = [report for report in hidden if not report.ok]
    for theme in dict.fromkeys(report.case.theme for report in failed):
        reports = [report for report in failed if report.case.theme == theme]
        total = sum(report.case.theme == theme for report in hidden)
        causes = Counter(_hidden_cause(report) for report in reports)
        details = ", ".join(
            f"{count} × {cause}" if count > 1 else cause for cause, count in causes.items()
        )
        line = f"{len(reports)} raté(s) sur {total} : {details}"
        console.print(Text.assemble(("   • ", "red"), (f"{theme}", "bold"), f"  {line}"))


def _hidden_cause(report: CaseReport) -> str:
    """Explain a hidden failure without giving any value away."""
    outcome = report.outcome
    where = _location(outcome.error)
    match outcome.status:
        case "exception":
            return f"{outcome.error.type}{where}"
        case "timeout":
            return f"temps dépassé{where}"
        case "flood":
            return f"affichage sans fin{where}"
        case "crash":
            return "arrêt brutal de Python"
        case "skipped":
            return "non exécuté"
    if outcome.modified:
        return "un argument a été modifié"
    if report.case.has_value and not outcome.plain:
        return f"renvoie un objet {outcome.type_name}"
    return "mauvais résultat"


def _location(error: RunError | None) -> str:
    if error is None or error.file is None:
        return ""
    return f" ({error.file}, ligne {error.line})"


def _describe_case(case: Case) -> Text:
    if not case.is_program:
        text = Text(case.label)
        if case.after:
            text.append(f"\nvaleur de {case.after} après l'appel", style="dim")
        if case.stdin:
            text.append("\nsaisies : " + " ⏎ ".join(case.stdin), style="dim")
        return text
    typed = " ⏎ ".join(repr(line) if not line else line for line in case.stdin) or "aucune"
    details = f"\nsaisies : {typed}"
    if case.seed is not None:
        details += f"\ngraine aléatoire : {case.seed}"
    return Text.assemble(case.label, (details, "dim"))


def _describe_expected(case: Case) -> Text:
    parts = []
    if case.has_value:
        parts.append(_show_value(case.value))
    if case.output is not None:
        parts.append(_shorten(normalize_output(case.output)) or "(rien)")
    return Text("\n".join(parts))


def _describe_outcome(report: CaseReport) -> Text:
    case, outcome = report.case, report.outcome
    if outcome.status != "value":
        return _describe_failure(outcome)
    parts = []
    if case.control is not None:
        parts.append(_show_value(report.observed))
    elif case.has_value:
        parts.append(_shorten(outcome.shown))
        if not outcome.plain:
            parts.append(f"(objet {outcome.type_name})")
        elif type(outcome.value) is not type(case.value) and not report.ok:
            parts.append(f"(type {outcome.type_name})")
    if case.output is not None:
        parts.append(_shorten(normalize_output(outcome.output)) or "(rien)")
    text = Text("\n".join(parts))
    if outcome.modified:
        names = ", ".join(_argument_name(case, item) for item in outcome.modified)
        text.append(f"\nl'argument « {names} » a été modifié", style="red")
    return text


def _show_value(value: object) -> str:
    """Write a value, as plain text if it spreads over several lines."""
    if isinstance(value, str) and "\n" in value:
        return _shorten(value)
    return _shorten(repr(value))


def _argument_name(case: Case, item: int | str) -> str:
    if isinstance(item, str):
        return item
    names = case.function.parameters
    return names[item] if item < len(names) else str(item + 1)


def _describe_failure(outcome: Outcome) -> Text:
    error = outcome.error
    match outcome.status:
        case "skipped":
            return Text("non exécuté (trop de temps dépassés)", style="yellow")
        case "timeout":
            text = Text("temps dépassé : boucle infinie ?", style="red")
        case "flood":
            text = Text("affichage sans fin : boucle infinie ?", style="red")
        case "crash":
            text = Text(f"arrêt brutal de Python : {error.message}", style="red")
        case _:
            text = Text(_error_title(error), style="red")
    if outcome.during_import:
        text.append("\npendant l'import du module")
    if error is not None and error.file:
        text.append(f"\n{error.file}, ligne {error.line}", style="cyan")
        if error.source:
            text.append(f"\n{error.source}", style="dim")
    if outcome.output.strip() and outcome.status == "exception":
        text.append(f"\naffiché avant : {_shorten(normalize_output(outcome.output))}", style="dim")
    return text


def _error_title(error: RunError) -> str:
    if error.type == "EOFError" and error.message == "EOF when reading a line":
        return "EOFError : ton programme demande plus de saisies que prévu"
    if error.type == "RecursionError":
        return "RecursionError : récursion sans fin ?"
    return f"{error.type} : {error.message}" if error.message else error.type


def _show_quality(console: Console, remarks: list[Problem]) -> None:
    detail = "aucune remarque" if not remarks else f"{len(remarks)} remarque(s), non bloquant"
    console.print(_title(4, "Qualité", _OK if not remarks else None, detail))
    for group in GROUPS:
        selected = [remark for remark in remarks if remark.group == group]
        if selected:
            console.print(Text(f"   {group}", style="bold yellow"))
        for remark in selected:
            console.print(_bullet(remark, "yellow"))


def _shorten(text: str) -> str:
    return text if len(text) <= MAX_SHOWN else text[:MAX_SHOWN] + "…"
