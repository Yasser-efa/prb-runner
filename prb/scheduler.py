"""Spaced repetition: what the history of an exercise implies, and what to do next.

A *cycle* goes from the moment an exercise is started (or started again for a review) to its
success. A success plans the next review after 3 days, then 7, then 21. A review that is not
passed on the day it was started goes back to the first interval.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from enum import Enum

from prb.progress import Attempt, History, Session

INTERVALS = (3, 7, 21)
NEW_PER_REVIEW = 2


class Stage(Enum):
    """Where the student stands with an exercise."""

    NEW = "à faire"
    ACTIVE = "en cours"
    PLANNED = "réussi"
    DONE = "acquis"


@dataclass
class State:
    """Summary of the history of an exercise."""

    exercise_id: str
    stage: Stage = Stage.NEW
    level: int = 0
    due_on: date | None = None
    urgent: bool = False
    cycle_start: datetime | None = None
    cycle_kind: str = "new"
    solution_seen: bool = False
    passed_at: datetime | None = None
    last_seen: datetime | None = None
    seconds: int | None = None
    attempts: int = 0
    hints: int = 0

    def is_due(self, today: date) -> bool:
        """Tell whether a review is planned today or earlier."""
        return self.stage is Stage.PLANNED and self.due_on is not None and self.due_on <= today


@dataclass(frozen=True)
class Choice:
    """The exercise to work on. ``kind`` is "new", "review" or "resume"."""

    state: State
    kind: str


def read_state(history: History) -> State:
    """Replay the history of an exercise.

    :param history: the facts
    :return: the current state
    """
    state = State(history.exercise_id, attempts=len(history.attempts))
    events: list[tuple[datetime, int, object]] = []
    events += [(session.started_at, 0, session) for session in history.sessions]
    events += [(moment, 1, moment) for moment in history.solutions_viewed]
    events += [(attempt.at, 2, attempt) for attempt in history.attempts]
    for moment, _, event in sorted(events, key=lambda item: item[:2]):
        state.last_seen = max(moment, state.last_seen or moment)
        if isinstance(event, Session):
            _start(state, event)
        elif isinstance(event, Attempt):
            _attempt(state, event)
        elif state.stage is not Stage.PLANNED and state.stage is not Stage.DONE:
            state.solution_seen = True
    if state.stage is Stage.ACTIVE:
        state.seconds = elapsed_seconds(history, state)
    state.hints = len({hint.level for hint in cycle_hints(history, state)})
    return state


def cycle_hints(history: History, state: State) -> list:
    """List the hints displayed since the exercise was last started.

    :param history: the facts
    :param state: the state computed from them
    :return: the hints, oldest first
    """
    start = state.cycle_start
    return [hint for hint in history.hints if start is None or hint.at >= start]


def elapsed_seconds(history: History, state: State) -> int | None:
    """Add up the sessions of the current cycle.

    :param history: the facts
    :param state: the state computed from them
    :return: the time in seconds, None if the chronometer was never started
    """
    sessions = [
        session
        for session in history.sessions
        if state.cycle_start is not None and session.started_at >= state.cycle_start
    ]
    if not sessions:
        return None
    return round(sum((session.duration for session in sessions), timedelta()).total_seconds())


def choose(
    states: Sequence[State], histories: Sequence[History], today: date, wanted: str | None = None
) -> Choice | None:
    """Choose the exercise of the day.

    An unfinished exercise comes first. Otherwise one review is proposed after two new
    exercises, as long as both exist.

    :param states: the state of every exercise, in the order of the bank
    :param histories: their histories
    :param today: the current date
    :param wanted: "new" or "review" to force the choice
    :return: the choice, None if there is nothing to do
    """
    active = [state for state in states if state.stage is Stage.ACTIVE]
    new = [Choice(state, "new") for state in states if state.stage is Stage.NEW]
    due = [state for state in states if state.is_due(today)]
    reviews = [Choice(state, "review") for state in sorted(due, key=lambda s: s.due_on)]
    if wanted == "new":
        return new[0] if new else None
    if wanted == "review":
        planned = [state for state in states if state.stage is Stage.PLANNED]
        planned.sort(key=lambda state: state.due_on)
        return Choice(planned[0], "review") if planned else None
    if active:
        return Choice(max(active, key=lambda state: state.last_seen), "resume")
    urgent = [choice for choice in reviews if choice.state.urgent]
    if urgent:
        return urgent[0]
    if reviews and (not new or _new_since_review(histories) >= NEW_PER_REVIEW):
        return reviews[0]
    return new[0] if new else None


def current_exercise(states: Sequence[State]) -> str | None:
    """Find the exercise the student is working on.

    :param states: the state of every exercise
    :return: the unfinished exercise seen last, or else the exercise seen last
    """
    seen = [state for state in states if state.last_seen is not None]
    if not seen:
        return None
    active = [state for state in seen if state.stage is Stage.ACTIVE]
    return max(active or seen, key=lambda state: state.last_seen).exercise_id


def _start(state: State, session: Session) -> None:
    """Open a cycle, unless one is already open."""
    if state.stage is Stage.ACTIVE:
        return
    state.cycle_kind = "new" if state.stage is Stage.NEW else "review"
    state.stage = Stage.ACTIVE
    state.cycle_start = session.started_at
    state.solution_seen = state.solution_seen and state.cycle_kind == "new"
    state.due_on, state.urgent, state.passed_at = None, False, None


def _attempt(state: State, attempt: Attempt) -> None:
    if state.stage in (Stage.PLANNED, Stage.DONE):
        return  # The student is polishing a solution that already passed.
    if state.stage is Stage.NEW:
        # Verified without du_jour: the cycle covers the whole day.
        state.stage, state.cycle_kind = Stage.ACTIVE, "new"
        state.cycle_start = datetime.combine(attempt.at.date(), time.min)
    if not attempt.passed:
        return
    state.passed_at, state.seconds = attempt.at, attempt.seconds
    if state.solution_seen:
        _plan(state, level=0, due_on=attempt.at.date() + timedelta(days=1))
        state.urgent = True
        return
    same_day = state.cycle_start.date() == attempt.at.date()
    level = state.level + 1 if state.cycle_kind == "review" and same_day else 1
    if level > len(INTERVALS):
        state.stage, state.level, state.due_on = Stage.DONE, level, None
    else:
        _plan(state, level, attempt.at.date() + timedelta(days=INTERVALS[level - 1]))


def _plan(state: State, level: int, due_on: date) -> None:
    state.stage, state.level, state.due_on, state.urgent = Stage.PLANNED, level, due_on, False


def _new_since_review(histories: Sequence[History]) -> int:
    """Count the new exercises started since the last review."""
    kinds = [
        (session.started_at, session.kind)
        for history in histories
        for session in history.sessions
        if session.kind in ("new", "review")
    ]
    count = 0
    for _, kind in sorted(kinds, reverse=True):
        if kind == "review":
            return count
        count += 1
    return count
