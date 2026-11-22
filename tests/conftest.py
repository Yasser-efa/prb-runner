"""A tiny bank, built around an invented exercise, for the tests of the engine."""

from pathlib import Path

import pytest

from prb.bank import Exercise, load_exercise
from prb.paths import Paths

FUNCTION = '''titre = "Table"
reference = "test"
sorte = "fonction"

[organisation]
fichiers = ["tables.py"]

[[fonctions]]
module = "tables"
signature = "table(nombre: int, taille: int = 3) -> list[int]"
'''
VISIBLE = '''[[tests]]
appel = "table(2)"
attendu = "[2, 4, 6]"

[[tests]]
appel = "table(5, taille=2)"
attendu = "[5, 10]"
'''
HIDDEN = '''[[groupes]]
theme = "valeurs limites"
appels = ["table(0)", "table(7, 0)"]
'''
SOLUTION = '''"""Tables de multiplication."""


def table(nombre: int, taille: int = 3) -> list[int]:
    """
    Calcule les premiers multiples d'un nombre.

    :param nombre: le nombre à multiplier
    :param taille: la quantité de multiples
    :return: les multiples, du plus petit au plus grand
    """
    return [nombre * rang for rang in range(1, taille + 1)]
'''


class Workshop:
    """Writes exercises and student files in a temporary project."""

    def __init__(self, root: Path) -> None:
        self.paths = Paths(root)
        self.student = self.paths.solutions / "demo"

    def exercise(
        self,
        description: str = FUNCTION,
        visible: str = VISIBLE,
        hidden: str = HIDDEN,
        solution: dict[str, str] | None = None,
    ) -> Exercise:
        public = self.paths.exercises / "demo"
        private = self.paths.private / "demo"
        self.write(self.paths.exercises, {"ordre.toml": 'ordre = ["demo"]\n'})
        self.write(
            public,
            {"exercice.toml": description, "enonce.md": "# Demo\n", "tests_visibles.toml": visible},
        )
        self.write(private, {"tests_caches.toml": hidden, "indices.toml": 'indices = ["un"]\n'})
        self.write(private / "solution", solution or {"tables.py": SOLUTION})
        return load_exercise(self.paths, "demo")

    def submit(self, files: dict[str, str] | str) -> Path:
        """Write the student's files; a single text goes to tables.py."""
        if isinstance(files, str):
            files = {"tables.py": files}
        self.write(self.student, files)
        return self.student

    @staticmethod
    def write(folder: Path, files: dict[str, str]) -> None:
        for name, text in files.items():
            path = folder / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")


@pytest.fixture
def workshop(tmp_path: Path) -> Workshop:
    return Workshop(tmp_path)
