"""What each command does."""

from dataclasses import dataclass
from datetime import datetime

from rich.console import Console
from rich.text import Text

from prb import pycharm, report, screens
from prb.bank import load_exercise, load_order
from prb.model import BankError, Exercise
from prb.paths import Paths
from prb.progress import SESSION_MINUTES, History, Progress
from prb.scheduler import (
    Choice,
    Stage,
    State,
    choose,
    current_exercise,
    cycle_hints,
    elapsed_seconds,
    read_state,
)
from prb.validation import check_order, validate_bank
from prb.verdict import verify
from prb.workspace import archive_folder, own_files, prepare_folder

EXTRA_MINUTES = 30


class CommandError(Exception):
    """The command cannot be carried out."""


@dataclass
class Context:
    """What every command needs."""

    paths: Paths
    console: Console
    progress: Progress
    now: datetime

    def history(self, exercise_id: str) -> History:
        """Read the history of an exercise."""
        return self.progress.history(exercise_id)

    def state(self, exercise_id: str) -> State:
        """Compute the state of an exercise."""
        return read_state(self.history(exercise_id))

    def exercise(self, exercise_id: str | None) -> Exercise:
        """Load an exercise, by default the one the student is working on."""
        if exercise_id is None:
            states = [self.state(name) for name in load_order(self.paths)]
            exercise_id = current_exercise(states)
            if exercise_id is None:
                raise CommandError("aucun exercice en cours : lance d'abord « du_jour »")
        return load_exercise(self.paths, exercise_id)


def show_today(context: Context, wanted: str | None, exercise_id: str | None = None) -> int:
    """Start or resume the exercise of the day.

    :param context: the paths, the terminal and the progress
    :param wanted: "new", "review", "next" or None to let the tool decide
    :param exercise_id: the exercise chosen by the student, None to let the tool decide
    :return: the exit code
    """
    if exercise_id is not None:
        return _start_chosen(context, exercise_id)
    histories = [context.history(name) for name in load_order(context.paths)]
    states = [read_state(history) for history in histories]
    today = context.now.date()
    active = any(state.stage is Stage.ACTIVE for state in states)
    if wanted is None and not active and _finished_today(context, states):
        return 0
    forced = wanted if wanted in ("new", "review") else None
    choice = choose(states, histories, today, forced)
    if choice is None:
        _explain_nothing_to_do(context, states, forced)
        return 0
    _start(context, choice)
    return 0


def _start_chosen(context: Context, exercise_id: str) -> int:
    """Start or resume the exercise chosen by the student."""
    state = context.state(exercise_id)
    if state.stage in (Stage.PLANNED, Stage.DONE) and not state.is_due(context.now.date()):
        warning = (
            f"{exercise_id} est déjà réussi ({_next_review(state)}). Le recommencer maintenant "
            "compte comme une révision et range ton code dans mes_solutions/_archives/."
        )
        if not _confirm(context, warning, "Tape OUI pour le recommencer : "):
            context.console.print("Exercice non relancé.")
            return 1
    kind = {Stage.NEW: "new", Stage.ACTIVE: "resume"}.get(state.stage, "review")
    _start(context, Choice(state, kind))
    return 0


def _finished_today(context: Context, states: list[State]) -> bool:
    """Tell the student that the exercise of the day is done, if it is."""
    today = context.now.date()
    passed = [state for state in states if state.passed_at and state.passed_at.date() == today]
    if not passed:
        return False
    names = ", ".join(state.exercise_id for state in passed)
    context.console.print(Text(f"Déjà réussi aujourd'hui : {names}", style="bold green"))
    context.console.print("Pour en faire un autre : python -m prb du_jour --suivant")
    return True


def _explain_nothing_to_do(context: Context, states: list[State], forced: str | None) -> None:
    planned = [state for state in states if state.stage is Stage.PLANNED]
    if forced == "new":
        message = "Il n'y a plus de nouvel exercice."
    elif forced == "review":
        message = "Aucune révision n'est prévue."
    elif planned:
        state = min(planned, key=lambda item: item.due_on)
        date = screens.format_date(state.due_on)
        message = f"Rien à faire aujourd'hui. Prochaine révision : {state.exercise_id}, {date}."
    else:
        message = "Tous les exercices sont acquis."
    context.console.print(Text(message, style="bold"))


def _start(context: Context, choice: Choice) -> None:
    exercise = load_exercise(context.paths, choice.state.exercise_id)
    if choice.kind == "review":
        archive = archive_folder(context.paths, exercise, context.now)
        if archive is not None:
            name = archive.relative_to(context.paths.root).as_posix()
            context.console.print(Text(f"Ton code précédent est rangé dans {name}/", style="dim"))
    prepare_folder(context.paths, exercise, restore=True)
    pycharm.configure(context.paths.root, exercise.id)
    limit = max(SESSION_MINUTES, exercise.minutes + EXTRA_MINUTES)
    context.progress.start_session(exercise.id, choice.kind, context.now, limit)
    seconds = choice.state.seconds if choice.kind == "resume" else None
    screens.show_exercise(context.console, exercise, choice.kind, seconds, context.now)
    _show_others(context, exercise.id)


def _show_others(context: Context, exercise_id: str) -> None:
    """Remind the student of the other unfinished exercises."""
    for name in load_order(context.paths):
        if name != exercise_id and context.state(name).stage is Stage.ACTIVE:
            message = f"Aussi en cours : {name} (pour y revenir : python -m prb du_jour {name})"
            context.console.print(Text(message, style="dim"))


def verify_exercise(context: Context, exercise_id: str | None) -> int:
    """Verify the student's code and record the attempt.

    :param context: the paths, the terminal and the progress
    :param exercise_id: the exercise, None for the current one
    :return: the exit code, 0 if the exercise is passed
    """
    exercise = context.exercise(exercise_id)
    folder = prepare_folder(context.paths, exercise)
    pycharm.configure(context.paths.root, exercise.id)
    before = context.state(exercise.id)
    verdict = verify(exercise, folder)
    footer = []
    if own_files(folder, exercise):
        seconds = None
        if before.stage is Stage.ACTIVE:
            context.progress.touch_session(exercise.id, context.now)
            seconds = elapsed_seconds(context.history(exercise.id), before)
        context.progress.record_attempt(verdict, context.now, seconds)
        after = context.state(exercise.id)
        if seconds is not None:
            spent = screens.format_duration(seconds)
            footer.append(f"temps : {spent} (objectif : {exercise.minutes} min)")
        footer.append(f"tentative n° {after.attempts}")
        if verdict.passed:
            footer.append(_next_review(after))
    report.show_verdict(context.console, verdict, " · ".join(footer))
    return 0 if verdict.passed else 1


def _next_review(state: State) -> str:
    if state.stage is Stage.DONE:
        return "exercice acquis"
    return f"prochaine révision : {screens.format_date(state.due_on)}"


def show_hint(context: Context, exercise_id: str | None) -> int:
    """Display the next hint of an exercise.

    :param context: the paths, the terminal and the progress
    :param exercise_id: the exercise, None for the current one
    :return: the exit code
    """
    exercise = context.exercise(exercise_id)
    if not exercise.hints:
        raise CommandError(f"{exercise.id} n'a pas d'indice")
    history = context.history(exercise.id)
    state = read_state(history)
    level = max((hint.level for hint in cycle_hints(history, state)), default=0) + 1
    if level > len(exercise.hints):
        for number in range(1, len(exercise.hints) + 1):
            screens.show_hint(context.console, exercise, number)
        context.console.print("Tu as vu tous les indices.")
        return 0
    context.progress.record_hint(exercise.id, level, context.now)
    if state.stage is Stage.ACTIVE:
        context.progress.touch_session(exercise.id, context.now)
    screens.show_hint(context.console, exercise, level)
    remaining = len(exercise.hints) - level
    if remaining:
        context.console.print(f"Il reste {remaining} indice(s). Réfléchis d'abord avec celui-ci.")
    return 0


def show_solution(context: Context, exercise_id: str | None) -> int:
    """Display the reference solution, after a confirmation if it is not deserved.

    :param context: the paths, the terminal and the progress
    :param exercise_id: the exercise, None for the current one
    :return: the exit code
    """
    exercise = context.exercise(exercise_id)
    state = context.state(exercise.id)
    if state.stage not in (Stage.PLANNED, Stage.DONE):
        warning = (
            f"{exercise.id} n'est pas encore réussi. Si tu regardes la solution, l'exercice "
            "reviendra le lendemain de ta réussite."
        )
        if not _confirm(context, warning, "Tape OUI pour la voir quand même : "):
            context.console.print("Solution non affichée. Essaie plutôt : python -m prb indice")
            return 1
    context.progress.record_solution_viewed(exercise.id, context.now)
    screens.show_solution(context.console, exercise, exercise.reference_folder)
    return 0


def _confirm(context: Context, warning: str, question: str) -> bool:
    context.console.print(Text(warning))
    try:
        answer = input(question)
    except EOFError:
        return False
    return answer.strip().upper() == "OUI"


def show_progress(context: Context) -> int:
    """Display the table of all the exercises.

    :param context: the paths, the terminal and the progress
    :return: the exit code
    """
    exercises = [load_exercise(context.paths, name) for name in load_order(context.paths)]
    states = [context.state(exercise.id) for exercise in exercises]
    screens.show_progress(context.console, exercises, states, context.now.date())
    return 0


def validate(context: Context, wanted: list[str]) -> int:
    """Check the exercises of the bank.

    :param context: the paths, the terminal and the progress
    :param wanted: identifiers to check, all of them if empty
    :return: the exit code, 0 if everything is valid
    """
    console = context.console
    problems = [] if wanted else check_order(context.paths)
    for problem in problems:
        console.print(Text(f"✗ {problem}", style="red"))
    total = valid = 0
    for result in validate_bank(context.paths, wanted):
        total += 1
        valid += not result.problems
        screens.show_validation(console, result)
    console.print(Text(f"{valid}/{total} exercices valides", style="bold"))
    return 0 if valid == total and not problems else 1


ERRORS = (BankError, CommandError)
