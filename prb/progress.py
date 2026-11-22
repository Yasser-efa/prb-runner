"""History of the student's work, kept in SQLite.

Only facts are stored (sessions, attempts, hints, solutions displayed). What they imply,
such as the date of the next review, is computed by scheduler.py.
"""

import sqlite3
from collections.abc import Iterator
from contextlib import closing, contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from prb.verdict import Status, Verdict

SESSION_MINUTES = 90

_SCHEMA = """
CREATE TABLE IF NOT EXISTS attempts (
    id INTEGER PRIMARY KEY,
    exercise_id TEXT NOT NULL,
    at TEXT NOT NULL,
    seconds INTEGER,
    status TEXT NOT NULL,
    visible_ok INTEGER NOT NULL,
    visible_total INTEGER NOT NULL,
    hidden_ok INTEGER NOT NULL,
    hidden_total INTEGER NOT NULL,
    remarks INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS attempts_by_exercise ON attempts (exercise_id, at);
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY,
    exercise_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    started_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    limit_minutes INTEGER NOT NULL DEFAULT 90
);
CREATE INDEX IF NOT EXISTS sessions_by_exercise ON sessions (exercise_id, started_at);
CREATE TABLE IF NOT EXISTS hints (
    id INTEGER PRIMARY KEY,
    exercise_id TEXT NOT NULL,
    level INTEGER NOT NULL,
    at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS solutions_viewed (
    id INTEGER PRIMARY KEY,
    exercise_id TEXT NOT NULL,
    at TEXT NOT NULL
);
"""


@dataclass(frozen=True)
class Attempt:
    """One run of ``verifier``."""

    exercise_id: str
    at: datetime
    seconds: int | None
    status: Status
    visible_ok: int
    visible_total: int
    hidden_ok: int
    hidden_total: int
    remarks: int

    @property
    def passed(self) -> bool:
        """Tell whether the attempt succeeded."""
        return self.status is Status.PASSED


@dataclass(frozen=True)
class Session:
    """One morning of work on an exercise, started by ``du_jour``.

    ``kind`` is "new", "review" or "resume".
    """

    exercise_id: str
    kind: str
    started_at: datetime
    last_seen_at: datetime
    limit_minutes: int = SESSION_MINUTES

    @property
    def duration(self) -> timedelta:
        """Time spent, limited in case the student came back much later."""
        limit = timedelta(minutes=self.limit_minutes)
        return min(self.last_seen_at - self.started_at, limit)


@dataclass(frozen=True)
class Hint:
    """A hint that was displayed."""

    exercise_id: str
    level: int
    at: datetime


@dataclass(frozen=True)
class History:
    """All the facts about one exercise, oldest first."""

    exercise_id: str
    sessions: tuple[Session, ...] = ()
    attempts: tuple[Attempt, ...] = ()
    hints: tuple[Hint, ...] = ()
    solutions_viewed: tuple[datetime, ...] = ()


class Progress:
    """Access to the progress database."""

    def __init__(self, path: Path) -> None:
        self.path = path
        with self._connect() as connection:
            connection.executescript(_SCHEMA)
            columns = {row["name"] for row in connection.execute("PRAGMA table_info(sessions)")}
            if "limit_minutes" not in columns:
                connection.execute(
                    "ALTER TABLE sessions"
                    f" ADD COLUMN limit_minutes INTEGER NOT NULL DEFAULT {SESSION_MINUTES}"
                )

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        # sqlite3's own context manager commits but does not close the file.
        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.row_factory = sqlite3.Row
            yield connection

    def _query(self, query: str, *parameters: str) -> list[sqlite3.Row]:
        with self._connect() as connection:
            return connection.execute(query, parameters).fetchall()

    def record_attempt(self, verdict: Verdict, at: datetime, seconds: int | None) -> None:
        """Save the result of a verification.

        :param verdict: the result
        :param at: when it happened
        :param seconds: time spent on the exercise so far, None if it was not measured
        """
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO attempts (exercise_id, at, seconds, status, visible_ok,"
                " visible_total, hidden_ok, hidden_total, remarks)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    verdict.exercise.id,
                    _write(at),
                    seconds,
                    verdict.status.value,
                    sum(report.ok for report in verdict.visible),
                    len(verdict.visible),
                    sum(report.ok for report in verdict.hidden),
                    len(verdict.hidden),
                    len(verdict.remarks),
                ),
            )

    def start_session(
        self, exercise_id: str, kind: str, at: datetime, limit_minutes: int = SESSION_MINUTES
    ) -> None:
        """Start the chronometer, or let it run if the exercise is resumed on the same day.

        :param exercise_id: the exercise
        :param kind: "new", "review" or "resume"
        :param at: current time
        :param limit_minutes: longest time that the session can count for
        """
        if kind == "resume" and self.touch_session(exercise_id, at):
            return
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO sessions"
                " (exercise_id, kind, started_at, last_seen_at, limit_minutes)"
                " VALUES (?, ?, ?, ?, ?)",
                (exercise_id, kind, _write(at), _write(at), limit_minutes),
            )

    def touch_session(self, exercise_id: str, at: datetime) -> bool:
        """Note that the student is still working on today's session.

        :param exercise_id: the exercise
        :param at: current time
        :return: False if no session was started today, or if another exercise was started since
        """
        with self._connect() as connection:
            row = connection.execute(
                "SELECT id, started_at, last_seen_at FROM sessions WHERE exercise_id = ?"
                " ORDER BY started_at DESC, id DESC LIMIT 1",
                (exercise_id,),
            ).fetchone()
            if row is None or datetime.fromisoformat(row["started_at"]).date() != at.date():
                return False
            other = connection.execute(
                "SELECT id FROM sessions WHERE exercise_id != ? AND started_at >= ? LIMIT 1",
                (exercise_id, row["last_seen_at"]),
            ).fetchone()
            if other is not None:
                return False
            connection.execute(
                "UPDATE sessions SET last_seen_at = ? WHERE id = ?", (_write(at), row["id"])
            )
            return True

    def record_hint(self, exercise_id: str, level: int, at: datetime) -> None:
        """Note that a hint was displayed.

        :param exercise_id: the exercise
        :param level: number of the hint, starting at 1
        :param at: current time
        """
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO hints (exercise_id, level, at) VALUES (?, ?, ?)",
                (exercise_id, level, _write(at)),
            )

    def record_solution_viewed(self, exercise_id: str, at: datetime) -> None:
        """Note that the reference solution was displayed.

        :param exercise_id: the exercise
        :param at: current time
        """
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO solutions_viewed (exercise_id, at) VALUES (?, ?)",
                (exercise_id, _write(at)),
            )

    def history(self, exercise_id: str) -> History:
        """Gather everything that happened on an exercise.

        :param exercise_id: the exercise
        :return: its history
        """
        where = "WHERE exercise_id = ? ORDER BY"
        sessions = self._query(f"SELECT * FROM sessions {where} started_at, id", exercise_id)
        attempts = self._query(f"SELECT * FROM attempts {where} at, id", exercise_id)
        hints = self._query(f"SELECT * FROM hints {where} at, id", exercise_id)
        viewed = self._query(f"SELECT * FROM solutions_viewed {where} at, id", exercise_id)
        return History(
            exercise_id=exercise_id,
            sessions=tuple(_read_session(row) for row in sessions),
            attempts=tuple(_read_attempt(row) for row in attempts),
            hints=tuple(
                Hint(row["exercise_id"], row["level"], datetime.fromisoformat(row["at"]))
                for row in hints
            ),
            solutions_viewed=tuple(datetime.fromisoformat(row["at"]) for row in viewed),
        )


def _write(moment: datetime) -> str:
    return moment.isoformat(timespec="seconds")


def _read_session(row: sqlite3.Row) -> Session:
    return Session(
        row["exercise_id"],
        row["kind"],
        datetime.fromisoformat(row["started_at"]),
        datetime.fromisoformat(row["last_seen_at"]),
        row["limit_minutes"],
    )


def _read_attempt(row: sqlite3.Row) -> Attempt:
    values = {key: row[key] for key in row.keys() if key not in ("id", "at", "status")}
    return Attempt(at=datetime.fromisoformat(row["at"]), status=Status(row["status"]), **values)
