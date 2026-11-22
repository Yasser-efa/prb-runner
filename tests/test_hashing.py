import pytest

from prb.hashing import check_hashing
from prb.sources import read_sources


@pytest.fixture
def check(tmp_path):
    def run(code):
        (tmp_path / "code.py").write_text(f"{code}\n", encoding="utf-8")
        return [problem.message for problem in check_hashing(read_sources(tmp_path)["code.py"])]

    return run


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("x = {[1]}", "une liste ne peut pas être un élément d'ensemble"),
        ("x = {[1]: 2}", "une liste ne peut pas être une clé de dictionnaire"),
        ("x = {{1: 2}}", "un dictionnaire ne peut pas être un élément d'ensemble"),
        ("x = {{1}: 2}", "un ensemble ne peut pas être une clé de dictionnaire"),
        ("x = {(1, [2])}", "un tuple qui contient une liste"),
    ],
)
def test_messages(check, code, expected):
    (message,) = check(code)
    assert message.startswith(expected)


@pytest.mark.parametrize(
    "code",
    [
        "notes = {}\nnotes[[1]] = 2",
        "notes = dict()\nnotes[sorted('ba')] = 2",
        "notes = {}\nnotes.setdefault(sorted('ba'), [])",
        "vus = set()\nvus.add([1])",
        "vus = {1}\nvus.discard([1])",
        "x = {list('abc')}",
        "x = {sorted(mot) for mot in []}",
        "x = {mot.split(): 1 for mot in []}",
        "x = {element for element in [[1], [2]]}",
        "mots = input().split()\nx = {mots}",
        "liste = []\nliste += [1]\nx = {liste}",
        "liste = [1]\ncopie = liste\nx = {copie}",
        "liste = [1] * 3 + [2]\nx = {liste[:2]}",
        "MOTS = ['a']\n\n\ndef f():\n    return {MOTS}",
        "def f(mots: list[str]):\n    return {mots}",
        "def f(**options):\n    return {options}",
        "def f(mot):\n    mot = sorted(mot)\n    return {mot}",
        "def f():\n    return [1]\n\n\nx = {f()}",
        "def f(n) -> list[int]:\n    return n\n\n\nx = {f(1)}",
        "vus = set()\nfor ligne in [[1], [2]]:\n    vus.add(ligne)",
    ],
)
def test_certain_mistakes(check, code):
    assert len(check(code)) == 1


@pytest.mark.parametrize(
    "code",
    [
        "x = {1: [2], (1, 2): {3}, 'a': {}}",
        "x = {*[1, 2], len([3])}",
        "x = {**{1: 2}}",
        "x = {tuple([1]), str([1]), frozenset({1})}",
        "notes = {}\nnotes[1] = [2]",
        "liste = [1, 2]\nliste[0] = 3",
        "valeur = [1]\nvaleur = 3\nx = {valeur}",
        "valeur = [1]\nvaleur = tuple(valeur)\nx = {valeur}",
        "def f(valeur):\n    return {valeur}",
        "def f(*valeurs):\n    return {valeurs}",
        "def f(mot):\n    notes = {mot: 1}\n    mot = sorted(mot)\n    return mot, notes",
        "def f(grille):\n    vus = set()\n    for ligne in grille:\n        vus.add(ligne)\n",
        "MOTS = ['a']\n\n\ndef f(MOTS):\n    return {MOTS}",
        "def sorted(mot):\n    return 'a'\n\n\nx = {sorted('b')}",
        "def f():\n    yield [1]\n\n\nx = {f()}",
        "notes = {'a': 1}\nprint([1] in notes, notes.keys())",
        "compte = {}\nfor mot in input().split():\n    compte[mot] = compte.get(mot, 0) + 1",
    ],
)
def test_correct_or_uncertain_code(check, code):
    assert check(code) == []
