"""Progress of the student, kept in SQLite."""

import sqlite3
from collections.abc import Iterator
from contextlib import closing, contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from prb.verdict import Status, Verdict

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


class Progress:
    """Access to the progress database."""

    def __init__(self, path: Path) -> None:
        self.path = path
        with self._connect() as connection:
            connection.executescript(_SCHEMA)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        # sqlite3's own context manager commits but does not close the file.
        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.row_factory = sqlite3.Row
            yield connection

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
                    at.isoformat(timespec="seconds"),
                    seconds,
                    verdict.status.value,
                    sum(report.ok for report in verdict.visible),
                    len(verdict.visible),
                    sum(report.ok for report in verdict.hidden),
                    len(verdict.hidden),
                    len(verdict.remarks),
                ),
            )

    def attempts(self, exercise_id: str | None = None) -> list[Attempt]:
        """List the attempts, oldest first.

        :param exercise_id: keep only this exercise
        :return: the attempts
        """
        query = "SELECT * FROM attempts"
        parameters: tuple[str, ...] = ()
        if exercise_id is not None:
            query += " WHERE exercise_id = ?"
            parameters = (exercise_id,)
        with self._connect() as connection:
            rows = connection.execute(f"{query} ORDER BY at, id", parameters).fetchall()
        return [_read_attempt(row) for row in rows]


def _read_attempt(row: sqlite3.Row) -> Attempt:
    values = {key: row[key] for key in row.keys() if key not in ("id", "at", "status")}
    return Attempt(at=datetime.fromisoformat(row["at"]), status=Status(row["status"]), **values)
