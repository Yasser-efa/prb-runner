"""Locations of the project folders."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Paths:
    """Every folder the tool reads or writes, relative to one root."""

    root: Path

    @property
    def exercises(self) -> Path:
        """Public part of the bank."""
        return self.root / "exercices"

    @property
    def private(self) -> Path:
        """Reference solutions, hidden tests and hints."""
        return self.root / "_prive"

    @property
    def solutions(self) -> Path:
        """The student's own code, one folder per exercise."""
        return self.root / "mes_solutions"

    @property
    def archives(self) -> Path:
        """Previous code of the exercises under review."""
        return self.solutions / "_archives"

    @property
    def database(self) -> Path:
        """SQLite file holding the progress."""
        return self.root / "progression.sqlite3"


DEFAULT_PATHS = Paths(Path(__file__).resolve().parent.parent)
