"""Command line: ``python -m prb <commande>``."""

import argparse
import sys
from collections.abc import Sequence
from datetime import datetime

from rich.console import Console
from rich.text import Text

from prb import pycharm, report
from prb.bank import BankError, load_exercise, load_order
from prb.linting import RuffError
from prb.paths import DEFAULT_PATHS, Paths
from prb.progress import Progress
from prb.sources import list_files
from prb.verdict import verify


def main(arguments: Sequence[str] | None = None, paths: Paths = DEFAULT_PATHS) -> int:
    """Run a command.

    :param arguments: the words typed after ``python -m prb``
    :param paths: the project folders
    :return: the exit code, 0 if everything went well
    """
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    console = Console()
    options = _build_parser().parse_args(arguments)
    try:
        return options.run(options, paths, console)
    except (BankError, RuffError) as error:
        console.print(Text(f"Erreur : {error}", style="bold red"))
        return 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m prb", description="PRB Starters")
    commands = parser.add_subparsers(required=True, metavar="commande")
    command = commands.add_parser("verifier", help="vérifie ta solution")
    command.add_argument("id", nargs="?", help="exercice (par défaut : l'exercice en cours)")
    command.set_defaults(run=_verify)
    return parser


def _verify(options: argparse.Namespace, paths: Paths, console: Console) -> int:
    progress = Progress(paths.database)
    exercise = load_exercise(paths, options.id or _current_exercise(paths, progress))
    pycharm.configure(paths.root, exercise.id)
    folder = paths.solutions / exercise.id
    folder.mkdir(parents=True, exist_ok=True)
    verdict = verify(exercise, folder)
    footer = ""
    if list_files(folder):
        progress.record_attempt(verdict, datetime.now(), None)
        footer = f"tentative n° {len(progress.attempts(exercise.id))}"
    report.show_verdict(console, verdict, footer)
    return 0 if verdict.passed else 1


def _current_exercise(paths: Paths, progress: Progress) -> str:
    """Choose the last exercise attempted, or the first one that is not done."""
    attempts = progress.attempts()
    done = {attempt.exercise_id for attempt in attempts if attempt.passed}
    if attempts and not attempts[-1].passed:
        return attempts[-1].exercise_id
    for exercise_id in load_order(paths):
        if exercise_id not in done:
            return exercise_id
    raise BankError("tous les exercices sont réussis : précise un identifiant")
