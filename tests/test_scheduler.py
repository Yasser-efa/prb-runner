from datetime import date, datetime, timedelta

import pytest

from prb.progress import Attempt, Hint, History, Session
from prb.scheduler import (
    Stage,
    State,
    choose,
    current_exercise,
    elapsed_seconds,
    read_state,
)
from prb.verdict import Status

MONDAY = datetime(2026, 11, 23, 8, 0)


def at(days=0, minutes=0):
    return MONDAY + timedelta(days=days, minutes=minutes)


def session(kind, days=0, minutes=0, length=10, name="a"):
    start = at(days, minutes)
    return Session(name, kind, start, start + timedelta(minutes=length))


def attempt(days=0, minutes=30, passed=True, seconds=1800):
    status = Status.PASSED if passed else Status.FAILED
    return Attempt("a", at(days, minutes), seconds, status, 1, 1, 1, 1, 0)


def state(sessions=(), attempts=(), hints=(), viewed=()):
    return read_state(History("a", tuple(sessions), tuple(attempts), tuple(hints), tuple(viewed)))


def test_untouched_exercise():
    result = state()
    assert result.stage is Stage.NEW and result.due_on is None and result.last_seen is None


def test_started_exercise():
    result = state([session("new")], [attempt(passed=False)])
    assert result.stage is Stage.ACTIVE and result.attempts == 1 and result.seconds == 600


def test_success_plans_a_review_after_three_days():
    result = state([session("new")], [attempt(passed=False), attempt(minutes=40)])
    assert result.stage is Stage.PLANNED and result.level == 1
    assert result.due_on == date(2026, 11, 26) and result.seconds == 1800
    assert not result.is_due(date(2026, 11, 25)) and result.is_due(date(2026, 11, 26))


def test_success_on_the_second_day_counts_as_a_success():
    result = state([session("new"), session("resume", 1)], [attempt(1)])
    assert result.level == 1 and result.due_on == date(2026, 11, 27)


def test_intervals_then_done():
    sessions, attempts, dates = [], [], []
    day = 0
    for kind in ("new", "review", "review", "review"):
        sessions.append(session(kind, day))
        attempts.append(attempt(day))
        result = state(sessions, attempts)
        if result.due_on:
            dates.append((result.due_on - MONDAY.date()).days - day)
            day = (result.due_on - MONDAY.date()).days
    assert dates == [3, 7, 21]
    assert result.stage is Stage.DONE and result.due_on is None


def test_failed_review_goes_back_to_the_first_interval():
    sessions = [session("new"), session("review", 3), session("review", 10)]
    attempts = [attempt(), attempt(3), attempt(10, passed=False)]
    result = state(sessions, attempts)
    assert result.stage is Stage.ACTIVE and result.cycle_kind == "review"
    result = state([*sessions, session("resume", 11)], [*attempts, attempt(11)])
    assert result.level == 1 and result.due_on == date(2026, 12, 7)


def test_review_passed_after_mistakes_on_the_same_day_counts():
    sessions = [session("new"), session("review", 3)]
    result = state(sessions, [attempt(), attempt(3, 5, passed=False), attempt(3, 20)])
    assert result.level == 2 and result.due_on == date(2026, 12, 3)


def test_polishing_a_passed_exercise_changes_nothing():
    attempts = [attempt(), attempt(minutes=50, passed=False), attempt(1), attempt(2, passed=False)]
    result = state([session("new")], attempts)
    assert result.stage is Stage.PLANNED and result.due_on == date(2026, 11, 26)
    assert result.attempts == 4


def test_solution_seen_before_success_brings_the_exercise_back_the_next_day():
    result = state([session("new")], [attempt()], viewed=[at(minutes=10)])
    assert result.urgent and result.due_on == date(2026, 11, 24) and result.level == 0
    sessions = [session("new"), session("review", 1)]
    result = state(sessions, [attempt(), attempt(1)], viewed=[at(0, 9)])
    assert not result.urgent and result.level == 1 and result.due_on == date(2026, 11, 27)


def test_solution_seen_before_starting_counts_too():
    assert state([session("new", 1)], [attempt(1)], viewed=[at()]).urgent


def test_solution_seen_after_success_is_free():
    result = state([session("new")], [attempt()], viewed=[at(minutes=40)])
    assert not result.urgent and result.due_on == date(2026, 11, 26)
    result = state([session("new"), session("review", 3)], [attempt(), attempt(3)], viewed=[at(1)])
    assert result.level == 2


def test_verifying_without_du_jour():
    result = state(attempts=[attempt(passed=False, seconds=None)])
    assert result.stage is Stage.ACTIVE and result.seconds is None
    result = state(attempts=[attempt(seconds=None)])
    assert result.stage is Stage.PLANNED and result.seconds is None
    result = state([session("resume", minutes=40)], [attempt(passed=False, seconds=None)])
    assert result.seconds == 600


def test_sessions_add_up_and_are_limited():
    sessions = (session("new", length=40), session("resume", 1, length=600))
    history = History("a", sessions)
    assert elapsed_seconds(history, read_state(history)) == (40 + 90) * 60
    long = Session("a", "resume", at(2), at(2, 600), limit_minutes=180)
    history = History("a", (*sessions, long))
    assert elapsed_seconds(history, read_state(history)) == (40 + 90 + 180) * 60


def test_time_restarts_for_a_review():
    history = History("a", (session("new"), session("review", 3, length=7)), (attempt(),))
    assert elapsed_seconds(history, read_state(history)) == 7 * 60


def test_hints_restart_for_a_review():
    hints = (Hint("a", 1, at(0, 5)), Hint("a", 2, at(0, 6)), Hint("a", 1, at(3, 5)))
    assert state([session("new")], hints=hints[:2]).hints == 2
    assert state([session("new"), session("review", 3)], [attempt()], hints).hints == 1


# Choice of the exercise of the day


def make(name, stage=Stage.NEW, **values):
    return State(name, stage, **values)


def planned(name, days, **values):
    return make(name, Stage.PLANNED, level=1, due_on=at(days).date(), **values)


def picked(states, histories=(), wanted=None):
    choice = choose(states, histories, MONDAY.date(), wanted)
    return choice and (choice.state.exercise_id, choice.kind)


def started(*kinds):
    return [History("x", tuple(session(kind, day) for day, kind in enumerate(kinds)))]


def test_new_exercises_follow_the_order():
    assert picked([make("a"), make("b")]) == ("a", "new")
    assert picked([planned("a", 3), make("b")]) == ("b", "new")


def test_unfinished_exercise_comes_first():
    states = [make("a"), make("b", Stage.ACTIVE, last_seen=at(-1)), planned("c", -5)]
    assert picked(states) == ("b", "resume")


def test_last_seen_unfinished_exercise_wins():
    states = [make(n, Stage.ACTIVE, last_seen=at(d)) for n, d in (("a", -3), ("b", -1), ("c", -2))]
    assert picked(states) == ("b", "resume")


@pytest.mark.parametrize(
    ("kinds", "expected"),
    [
        ((), "new"),
        (("new",), "new"),
        (("new", "new"), "review"),
        (("new", "resume", "new"), "review"),
        (("new", "new", "review"), "new"),
        (("new", "new", "review", "new"), "new"),
        (("new", "new", "review", "new", "new"), "review"),
    ],
)
def test_one_review_for_two_new_exercises(kinds, expected):
    assert picked([planned("a", -1), make("b")], started(*kinds))[1] == expected


def test_reviews_when_nothing_is_new():
    assert picked([planned("a", 0), planned("b", -2)]) == ("b", "review")


def test_review_after_seeing_the_solution_is_urgent():
    assert picked([planned("a", -9), planned("b", 0, urgent=True), make("c")]) == ("b", "review")
    assert picked([planned("b", 1, urgent=True), make("c")]) == ("c", "new")


def test_nothing_to_do():
    assert picked([planned("a", 2), make("b", Stage.DONE)]) is None


def test_forced_choices():
    states = [make("a", Stage.ACTIVE, last_seen=at(-1)), planned("b", 9), make("c")]
    assert picked(states, wanted="new") == ("c", "new")
    assert picked(states, wanted="review") == ("b", "review")
    assert picked([make("a")], wanted="review") is None
    assert picked([planned("a", 0)], wanted="new") is None


def test_current_exercise():
    assert current_exercise([make("a")]) is None
    states = [planned("a", 3, last_seen=at(1)), make("b", Stage.ACTIVE, last_seen=at(0))]
    assert current_exercise(states) == "b"
    assert current_exercise(states[:1]) == "a"


def test_an_unfinished_exam_is_current_only_until_another_exercise_is_seen():
    exam = make("e", Stage.ACTIVE, last_seen=at(0))
    assert current_exercise([make("a"), exam], {"e"}) == "e"
    assert current_exercise([planned("a", 3, last_seen=at(1)), exam], {"e"}) == "a"
    assert current_exercise([make("a", Stage.ACTIVE, last_seen=at(-1)), exam], {"e"}) == "e"
