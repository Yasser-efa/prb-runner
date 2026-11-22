"""The real bank, used with an empty progress."""

import shutil
from datetime import datetime
from pathlib import Path

import pytest

from prb import cli
from prb.bank import load_daily_order, load_exams, load_order
from prb.paths import Paths
from prb.progress import Progress

ROOT = Path(__file__).parent.parent
EVENING = datetime(2026, 11, 22, 21, 15, 49)


@pytest.fixture
def paths(tmp_path):
    """Copy the bank, without the student's code and progress."""
    for name in ("exercices", "_prive"):
        shutil.copytree(ROOT / name, tmp_path / name)
    return Paths(tmp_path)


def test_empty_progress_proposes_alice_and_bob(paths, capsys):
    assert cli.main(["du_jour"], paths, EVENING) == 0
    output = capsys.readouterr().out
    assert "Nouvel exercice : alice_bob " in output and "Alice et Bob" in output
    assert len(Progress(paths.database).history("alice_bob").sessions) == 1


def test_an_unfinished_exam_does_not_replace_alice_and_bob(paths, capsys):
    started = EVENING.replace(minute=1, second=58)
    Progress(paths.database).start_session("examen_slam", "new", started, 150)
    assert cli.main(["du_jour"], paths, EVENING) == 0
    output = capsys.readouterr().out
    assert "Nouvel exercice : alice_bob " in output
    assert "Aussi en cours : examen_slam" in output
    (session,) = Progress(paths.database).history("examen_slam").sessions
    assert session.last_seen_at == started


def test_old_exams_are_the_exercises_on_demand(paths):
    exams = {name for name in load_order(paths) if name.startswith("examen_")}
    assert load_exams(paths) == exams and len(exams) == 5
    assert load_daily_order(paths)[0] == "alice_bob"
    assert not exams & set(load_daily_order(paths))
