"""Screens other than the verdict: exercise of the day, hints, solution, progress."""

from collections.abc import Sequence
from datetime import date, datetime
from pathlib import Path

from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from prb.bank import Exercise
from prb.scheduler import INTERVALS, Stage, State
from prb.sources import list_files
from prb.validation import Validation

_DAYS = ("lun.", "mar.", "mer.", "jeu.", "ven.", "sam.", "dim.")
_PREPARATION = """\
Avant de toucher au clavier, remplis la phase préparatoire **sur papier** :

- **QUOI** : entrées / variables, sorties / résultat attendu, constantes.
- **COMMENT** : un schéma sur un exemple *différent* de ceux de l'énoncé, avec les indices.
- **Justifications** : le type de chaque boucle et, pour un `while`, sa condition d'arrêt.
"""
_KINDS = {"new": "Nouvel exercice", "review": "Révision", "resume": "Suite"}


def show_exercise(
    console: Console, exercise: Exercise, kind: str, seconds: int | None, now: datetime
) -> None:
    """Display the statement, the layout, the reminder and the chronometer.

    :param console: the terminal
    :param exercise: the exercise
    :param kind: "new", "review" or "resume"
    :param seconds: time already spent on the exercise
    :param now: current time
    """
    console.print()
    console.rule(Text(f"{_KINDS[kind]} : {exercise.id}", style="bold"))
    console.print(Markdown(exercise.statement))
    console.print()
    console.print(Text("Fichiers à créer toi-même", style="bold"))
    console.print(layout_tree(exercise))
    console.print()
    title = "Phase préparatoire d'abord"
    console.print(Panel(Markdown(_PREPARATION), title=title, border_style="yellow"))
    if seconds:
        spent = f"Chrono relancé à {now:%H:%M} : {format_duration(seconds)} déjà passées"
    else:
        spent = f"Chrono lancé à {now:%H:%M}"
    console.print(Text(f"{spent} (objectif : {exercise.minutes} min)", style="bold cyan"))
    console.print(Text("Quand tu as fini : python -m prb verifier"))


def layout_tree(exercise: Exercise) -> Tree:
    """Draw the files that the student must create.

    :param exercise: the exercise
    :return: the tree
    """
    root = Tree(Text(f"mes_solutions/{exercise.id}/", style="cyan"))
    branches = {"": root}
    for name in sorted(exercise.files, key=lambda item: (item.count("/") == 0, item)):
        *folders, file = name.split("/")
        parent = ""
        for folder in folders:
            path = f"{parent}{folder}/"
            if path not in branches:
                branches[path] = branches[parent].add(Text(f"{folder}/", style="cyan"))
            parent = path
        branches[parent].add(Text(file))
    return root


def show_hint(console: Console, exercise: Exercise, level: int) -> None:
    """Display a hint.

    :param console: the terminal
    :param exercise: the exercise
    :param level: number of the hint, starting at 1
    """
    title = f"Indice {level}/{len(exercise.hints)} – {exercise.title}"
    console.print(Panel(Text(exercise.hints[level - 1]), title=title, border_style="yellow"))


def show_solution(console: Console, exercise: Exercise, folder: Path) -> None:
    """Display every file of the reference solution.

    :param console: the terminal
    :param exercise: the exercise
    :param folder: the folder of the solution
    """
    for name in list_files(folder):
        text = (folder / name).read_text(encoding="utf-8")
        console.rule(Text(f"{exercise.id}/{name}", style="bold"))
        console.print(Syntax(text, "python", line_numbers=True) if text.strip() else "(vide)")


def show_progress(
    console: Console, exercises: Sequence[Exercise], states: Sequence[State], today: date
) -> None:
    """Display the table of all the exercises.

    :param console: the terminal
    :param exercises: the bank
    :param states: the state of each exercise, in the same order
    :param today: the current date
    """
    table = Table(title="Progression", box=box.SIMPLE_HEAD)
    for column in ("", "Exercice", "Réf.", "Statut", "Essais", "Temps", "Ind.", "Révision"):
        right = column in ("", "Essais", "Temps", "Ind.")
        table.add_column(column, justify="right" if right else "left", no_wrap=column != "Réf.")
    for number, (exercise, state) in enumerate(zip(exercises, states, strict=True), 1):
        table.add_row(
            str(number),
            exercise.id,
            exercise.reference,
            describe_stage(state, today),
            str(state.attempts) if state.attempts else "–",
            format_duration(state.seconds) if state.seconds is not None else "–",
            f"{state.hints}/{len(exercise.hints)}" if state.hints else "–",
            describe_due(state, today),
        )
    console.print(table)
    done = sum(state.stage in (Stage.PLANNED, Stage.DONE) for state in states)
    due = sum(state.is_due(today) for state in states)
    summary = f"{done}/{len(states)} réussis, {due} révision(s) due(s)"
    active = [state.exercise_id for state in states if state.stage is Stage.ACTIVE]
    if active:
        summary += f", en cours : {', '.join(active)}"
    console.print(Text(summary))


def show_validation(console: Console, result: Validation) -> None:
    """Display the checking of one exercise.

    :param console: the terminal
    :param result: the result
    """
    mark, style = ("✗", "red") if result.problems else ("✓", "green")
    text = Text.assemble((f"{mark} ", style), f"{result.exercise_id:<26}")
    text.append(
        f"{result.visible} visibles, {result.hidden} cachés, {result.hints} indices", style="dim"
    )
    console.print(text)
    for problem in result.problems:
        console.print(Text(f"    • {problem}", style="red"))


def describe_stage(state: State, today: date) -> Text:
    """Write the status of an exercise.

    :param state: the state of the exercise
    :param today: the current date
    :return: the status, in colour
    """
    match state.stage:
        case Stage.NEW:
            return Text("à faire", style="dim")
        case Stage.ACTIVE:
            label = "en révision" if state.cycle_kind == "review" else "en cours"
            return Text(label, style="yellow")
        case Stage.DONE:
            return Text("acquis", style="bold green")
    if state.is_due(today):
        return Text("à revoir", style="magenta")
    if state.urgent:
        return Text("avec solution", style="yellow")
    return Text(f"réussi {state.level}/{len(INTERVALS) + 1}", style="green")


def describe_due(state: State, today: date) -> Text:
    """Write the date of the next review.

    :param state: the state of the exercise
    :param today: the current date
    :return: the date, in colour if it has come
    """
    if state.due_on is None:
        return Text("–")
    return Text(format_date(state.due_on), style="magenta" if state.is_due(today) else "")


def format_date(day: date) -> str:
    """Write a date in French.

    :param day: the date
    :return: for example "mer. 25/11"
    """
    return f"{_DAYS[day.weekday()]} {day:%d/%m}"


def format_duration(seconds: int) -> str:
    """Write a duration, rounded down to the minute.

    :param seconds: the duration
    :return: for example "32 min" or "1 h 05"
    """
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} min"
    return f"{minutes // 60} h {minutes % 60:02d}"
