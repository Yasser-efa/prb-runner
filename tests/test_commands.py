import io
import xml.etree.ElementTree as ElementTree
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from prb import cli
from prb.progress import Progress
from prb.screens import format_duration, layout_tree
from prb.workspace import WorkspaceError, archive_folder
from tests.conftest import SOLUTION

MONDAY = datetime(2026, 11, 23, 8, 0)
WRONG = "def table(nombre, taille=3):\n    return []\n"


@pytest.fixture
def run(workshop, capsys, monkeypatch):
    """Run a command at some moment and give what it displays."""
    monkeypatch.setenv("COLUMNS", "160")
    workshop.exercise()

    def execute(command, days=0, minutes=0):
        moment = MONDAY + timedelta(days=days, minutes=minutes)
        execute.code = cli.main(command.split(), workshop.paths, moment)
        return capsys.readouterr().out

    return execute


@pytest.fixture
def two_exercises(workshop, run):
    """Add a second exercise to the bank."""
    for folder in (workshop.paths.exercises, workshop.paths.private):
        for path in (folder / "demo").rglob("*"):
            if path.is_file():
                name = path.relative_to(folder / "demo").as_posix()
                workshop.write(folder / "autre", {name: path.read_text(encoding="utf-8")})
    workshop.write(workshop.paths.exercises, {"ordre.toml": 'ordre = ["demo", "autre"]\n'})


def test_exercise_of_the_day(workshop, run):
    output = run("du_jour")
    assert run.code == 0
    for part in ("Nouvel exercice : demo", "tables.py", "sur papier", "Chrono lancé à 08:00"):
        assert part in output
    assert "objectif : 40 min" in output
    assert workshop.student.is_dir() and not list(workshop.student.iterdir())
    assert "mes_solutions/demo" in next((workshop.paths.root / ".idea").glob("*.iml")).read_text()


def test_chronometer(workshop, run):
    run("du_jour")
    workshop.submit(WRONG)
    output = run("verifier", minutes=25)
    assert "temps : 25 min (objectif : 40 min)" in output and "tentative n° 1" in output
    assert run.code == 1
    output = run("du_jour", minutes=30)
    assert "Suite : demo" in output and "25 min déjà passées" in output
    output = run("du_jour", days=1)
    assert "Suite : demo" in output and "30 min déjà passées" in output
    workshop.submit(SOLUTION)
    output = run("verifier", days=1, minutes=10)
    assert "RÉUSSI" in output and "temps : 40 min" in output
    assert "prochaine révision : ven. 27/11" in output


def test_one_exercise_a_day(two_exercises, workshop, run):
    run("du_jour")
    workshop.submit(SOLUTION)
    run("verifier", minutes=20)
    output = run("du_jour", minutes=21)
    assert "Déjà réussi aujourd'hui : demo" in output and "--suivant" in output
    assert "Nouvel exercice : autre" in run("du_jour --suivant", minutes=22)
    assert "Suite : autre" in run("du_jour", minutes=23)


def test_chosen_exercise(two_exercises, workshop, run):
    output = run("du_jour autre")
    assert "Nouvel exercice : autre" in output and "Aussi en cours" not in output
    workshop.write(workshop.paths.solutions / "autre", {"tables.py": WRONG})
    run("verifier", minutes=10)
    assert "Suite : autre" in run("du_jour", days=1)
    workshop.write(workshop.paths.solutions / "autre", {"tables.py": SOLUTION})
    assert "RÉUSSI" in run("verifier", days=1, minutes=5)
    assert "Déjà réussi aujourd'hui : autre" in run("du_jour", days=1, minutes=6)
    assert "Nouvel exercice : demo" in run("du_jour demo", days=1, minutes=7)


def test_time_spent_on_another_exercise_does_not_count(two_exercises, workshop, run):
    run("du_jour")
    workshop.submit(WRONG)
    run("verifier", minutes=10)
    output = run("du_jour autre", minutes=20)
    assert "Aussi en cours : demo (pour y revenir : python -m prb du_jour demo)" in output
    output = run("du_jour demo", minutes=60)
    assert "Suite : demo" in output and "10 min déjà passées" in output
    assert "Aussi en cours : autre" in output and "Aussi en cours : demo" not in output
    assert "temps : 15 min" in run("verifier", minutes=65)
    run("du_jour autre", minutes=70)
    assert "temps : 15 min" in run("verifier demo", minutes=90)


@pytest.mark.parametrize(("answer", "restarted"), [("oui", True), ("non", False)])
def test_restarting_a_passed_exercise_needs_a_confirmation(
    workshop, run, monkeypatch, answer, restarted
):
    run("du_jour")
    workshop.submit(SOLUTION)
    run("verifier", minutes=20)
    monkeypatch.setattr("builtins.input", lambda _: answer)
    output = run("du_jour demo", minutes=30)
    assert "demo est déjà réussi (prochaine révision : jeu. 26/11)" in output
    assert ("Révision : demo" in output) is restarted
    assert (workshop.student / "tables.py").exists() is not restarted
    assert run.code == (0 if restarted else 1)
    assert ("en révision" in run("progression", minutes=31)) is restarted


def test_a_due_review_can_be_chosen_without_confirmation(workshop, run):
    run("du_jour")
    workshop.submit(SOLUTION)
    run("verifier", minutes=20)
    assert "Révision : demo" in run("du_jour demo", days=3)


def test_an_acquired_exercise_can_be_chosen_again(workshop, run, monkeypatch):
    for day in (0, 3, 10, 31):
        run("du_jour", days=day)
        workshop.submit(SOLUTION)
        run("verifier", days=day, minutes=20)
    monkeypatch.setattr("builtins.input", lambda _: "OUI")
    output = run("du_jour demo", days=40)
    assert "déjà réussi (exercice acquis)" in output and "Révision : demo" in output


def test_unknown_exercises_are_not_started(two_exercises, run):
    assert "exercice inconnu : dem (peut-être : demo)" in run("du_jour dem")
    assert run.code == 2
    assert "peut-être : autre" in run("du_jour autres")
    assert "peut-être" not in run("du_jour xyz")
    assert "en cours" not in run("progression")


def test_an_exercise_and_an_option_exclude_each_other(run):
    with pytest.raises(SystemExit):
        run("du_jour demo --nouveau")


def test_verifier_keeps_the_exercise_that_was_just_passed(two_exercises, workshop, run):
    run("du_jour")
    workshop.submit(SOLUTION)
    run("verifier", minutes=20)
    output = run("verifier", minutes=25)
    assert "RÉUSSI" in output and "tentative n° 2" in output
    assert "prochaine révision : jeu. 26/11" in output


def test_review_starts_from_an_empty_folder(workshop, run):
    run("du_jour")
    workshop.submit({"tables.py": SOLUTION, "brouillon/notes.txt": "a", ".idea/x": "b"})
    run("verifier", minutes=20)
    assert "Prochaine révision : demo, jeu. 26/11" in run("du_jour", days=1)
    output = run("du_jour", days=3)
    assert "Révision : demo" in output and "_archives/demo/2026-11-26_08h00" in output
    assert not list(workshop.student.iterdir())
    (archive,) = (workshop.paths.archives / "demo").iterdir()
    assert (archive / "tables.py").read_text(encoding="utf-8") == SOLUTION
    assert (archive / "brouillon/notes.txt").exists() and (archive / ".idea/x").exists()
    workshop.submit(WRONG)
    run("verifier", days=3, minutes=10)
    assert "Suite : demo" in run("du_jour", days=4)
    assert (workshop.student / "tables.py").exists()


def test_an_early_review_on_the_same_day_starts_a_new_cycle(workshop, run):
    run("du_jour")
    workshop.submit(SOLUTION)
    run("verifier", minutes=20)
    assert "Révision : demo" in run("du_jour --revision", minutes=30)
    assert "en révision" in run("progression", minutes=31)


def test_a_locked_file_stops_the_review(workshop, monkeypatch):
    exercise = workshop.exercise()
    workshop.submit(SOLUTION)

    def refuse(*_):
        raise PermissionError(13, "accès refusé")

    monkeypatch.setattr(Path, "rename", refuse)
    with pytest.raises(WorkspaceError, match="accès refusé"):
        archive_folder(workshop.paths, exercise, MONDAY)
    assert (workshop.student / "tables.py").exists()


def test_forced_choices(run):
    assert "Aucune révision" in run("du_jour --revision")
    run("du_jour")
    assert "plus de nouvel exercice" in run("du_jour --nouveau")


def test_hints_come_one_by_one(workshop, run):
    private = workshop.paths.private / "demo"
    workshop.write(private, {"indices.toml": 'indices = ["premier", "second"]\n'})
    run("du_jour")
    output = run("indice demo", minutes=5)
    assert "Indice 1/2" in output and "premier" in output and "second" not in output
    output = run("indice", minutes=6)
    assert "Indice 2/2" in output and "second" in output and "premier" not in output
    output = run("indice", minutes=7)
    assert "premier" in output and "second" in output and "tous les indices" in output
    assert "2/2" in run("progression", minutes=8)
    workshop.submit(SOLUTION)
    run("verifier", minutes=9)
    run("du_jour", days=3)
    assert "Indice 1/2" in run("indice", days=3, minutes=1)


def test_solution_needs_a_confirmation(workshop, run, monkeypatch):
    run("du_jour")
    monkeypatch.setattr("builtins.input", lambda _: "non")
    output = run("solution demo", minutes=5)
    assert run.code == 1 and "range(1" not in output
    monkeypatch.setattr("builtins.input", lambda _: " oui ")
    output = run("solution demo", minutes=6)
    assert run.code == 0 and "range(1" in output
    workshop.submit(SOLUTION)
    assert "prochaine révision : mar. 24/11" in run("verifier", minutes=7)
    assert "avec solution" in run("progression", minutes=8)
    assert "Révision : demo" in run("du_jour", days=1)


def test_solution_without_keyboard_is_refused(run, monkeypatch):
    def no_keyboard(_):
        raise EOFError

    monkeypatch.setattr("builtins.input", no_keyboard)
    assert "range(1" not in run("solution demo") and run.code == 1


def test_interruption(run, monkeypatch):
    def interrupt(_):
        raise KeyboardInterrupt

    monkeypatch.setattr("builtins.input", interrupt)
    assert "Interrompu" in run("solution demo") and run.code == 130


def test_solution_is_free_after_success(workshop, run):
    run("du_jour")
    workshop.submit(SOLUTION)
    run("verifier", minutes=5)
    assert "range(1" in run("solution", minutes=6)
    assert "réussi 1/4" in run("progression", minutes=7)


def test_progress_table(two_exercises, workshop, run):
    assert "0/2 réussis" in run("progression")
    run("du_jour")
    assert "en cours : demo" in run("progression", minutes=1)
    workshop.submit(SOLUTION)
    run("verifier", minutes=32)
    output = run("progression", days=1)
    for part in ("réussi 1/4", "32 min", "jeu. 26/11", "à faire", "1/2 réussis"):
        assert part in output
    output = run("progression", days=5)
    assert "à revoir" in output and "1 révision(s) due(s)" in output


def test_commands_without_a_current_exercise(run):
    for command in ("verifier", "indice", "solution"):
        assert "lance d'abord « du_jour »" in run(command)
        assert run.code == 2


def test_old_databases_are_completed(workshop):
    import sqlite3

    path = workshop.paths.root / "ancienne.sqlite3"
    with sqlite3.connect(path) as connection:
        connection.execute(
            "CREATE TABLE attempts (id INTEGER PRIMARY KEY, exercise_id TEXT NOT NULL,"
            " at TEXT NOT NULL, seconds INTEGER, status TEXT NOT NULL,"
            " visible_ok INTEGER NOT NULL, visible_total INTEGER NOT NULL,"
            " hidden_ok INTEGER NOT NULL, hidden_total INTEGER NOT NULL, remarks INTEGER NOT NULL)"
        )
        connection.execute(
            "INSERT INTO attempts VALUES (1, 'demo', '2026-11-22T18:00:00', NULL, 'réussi',"
            " 1, 1, 1, 1, 0)"
        )
    connection.close()
    progress = Progress(path)
    progress.start_session("demo", "review", MONDAY)
    assert progress.history("demo").attempts[0].passed
    assert len(progress.history("demo").sessions) == 1


def test_layout_is_drawn_as_a_tree(workshop):
    from rich.console import Console

    from tests.test_admissibility import GOOD, PACKAGE, VISIBLE

    exercise = workshop.exercise(PACKAGE, VISIBLE, "", GOOD)
    console = Console(width=80, record=True, file=io.StringIO())
    console.print(layout_tree(exercise))
    lines = [line.strip("├└─│ ") for line in console.export_text().splitlines()]
    assert lines == ["mes_solutions/demo/", "tables/", "__init__.py", "calculs.py", "main.py"]


@pytest.mark.parametrize(
    ("seconds", "text"), [(0, "0 min"), (59, "0 min"), (1920, "32 min"), (3900, "1 h 05")]
)
def test_durations(seconds, text):
    assert format_duration(seconds) == text


@pytest.mark.parametrize("name", ["du_jour", "verifier"])
def test_pycharm_run_configurations(name):
    root = Path(__file__).parent.parent
    tree = ElementTree.parse(root / ".run" / f"{name}.run.xml")
    options = {node.get("name"): node.get("value") for node in tree.iter("option")}
    assert options["SCRIPT_NAME"] == "prb" and options["MODULE_MODE"] == "true"
    assert options["PARAMETERS"] == name and options["ADD_SOURCE_ROOTS"] == "false"
