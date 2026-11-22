"""Command line: ``python -m prb <commande>``."""

import argparse
import sys
from collections.abc import Sequence
from datetime import datetime

from rich.console import Console
from rich.text import Text

from prb import commands
from prb.commands import Context
from prb.linting import RuffError
from prb.paths import DEFAULT_PATHS, Paths
from prb.progress import Progress
from prb.workspace import WorkspaceError


def main(
    arguments: Sequence[str] | None = None,
    paths: Paths = DEFAULT_PATHS,
    now: datetime | None = None,
) -> int:
    """Run a command.

    :param arguments: the words typed after ``python -m prb``
    :param paths: the project folders
    :param now: current time, for the tests
    :return: the exit code, 0 if everything went well
    """
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    options = _build_parser().parse_args(arguments)
    console = Console()
    moment = (now or datetime.now()).replace(microsecond=0)
    try:
        return options.run(Context(paths, console, Progress(paths.database), moment), options)
    except (*commands.ERRORS, RuffError, WorkspaceError) as error:
        console.print(Text(f"Erreur : {error}", style="bold red"))
        return 2
    except KeyboardInterrupt:
        console.print("\nInterrompu.")
        return 130


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m prb", description="PRB Starters")
    subparsers = parser.add_subparsers(required=True, metavar="commande")

    today = subparsers.add_parser("du_jour", help="affiche l'exercice du jour et lance le chrono")
    choice = today.add_mutually_exclusive_group()
    for option, value, text in (
        ("--suivant", "next", "passe à l'exercice suivant, même si celui du jour est réussi"),
        ("--nouveau", "new", "prend un nouvel exercice"),
        ("--revision", "review", "prend une révision"),
    ):
        choice.add_argument(option, dest="wanted", action="store_const", const=value, help=text)
    today.set_defaults(run=lambda context, options: commands.show_today(context, options.wanted))

    for name, function, text in (
        ("verifier", commands.verify_exercise, "vérifie ta solution"),
        ("indice", commands.show_hint, "affiche l'indice suivant"),
        ("solution", commands.show_solution, "affiche la solution de référence"),
    ):
        command = subparsers.add_parser(name, help=text)
        command.add_argument("id", nargs="?", help="exercice (par défaut : l'exercice en cours)")
        command.set_defaults(run=_with_exercise(function))

    validate = subparsers.add_parser("valider", help="vérifie la banque d'exercices")
    validate.add_argument("ids", nargs="*", metavar="id", help="exercices (par défaut : tous)")
    validate.set_defaults(run=lambda context, options: commands.validate(context, options.ids))

    progress = subparsers.add_parser("progression", help="affiche l'état de tous les exercices")
    progress.set_defaults(run=lambda context, _: commands.show_progress(context))
    return parser


def _with_exercise(function):
    return lambda context, options: function(context, options.id)
