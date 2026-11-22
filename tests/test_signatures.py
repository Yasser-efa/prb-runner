"""Functions that are missing or have another header: admissible, but their tests fail."""

import io

import pytest
from rich.console import Console

from prb.report import show_verdict
from prb.verdict import Status, verify
from tests.conftest import SOLUTION
from tests.test_admissibility import GOOD, MAIN, PACKAGE

DESCRIPTION = f'''{PACKAGE}
[[fonctions]]
module = "tables.calculs"
signature = "doubler(nombre: int) -> int"

[contraintes.fonctions.doubler]
imposes = ["while"]
'''
DOUBLER = '''

def doubler(nombre: int) -> int:
    """
    Double un nombre.

    :param nombre: le nombre
    :return: son double
    """
    while nombre:
        return nombre * 2
    return 0
'''
VISIBLE = '''[[tests]]
appel = "table(2)"
attendu = "[2, 4, 6]"

[[tests]]
appel = "doubler(4)"
attendu = "8"

[[tests]]
sortie = "[2, 4, 6]"
'''
HIDDEN = '[[groupes]]\ntheme = "secret"\nappels = ["table(987)", "doubler(654)"]\n'
COMPLETE = GOOD | {"tables/calculs.py": SOLUTION + DOUBLER}


@pytest.fixture
def check(workshop):
    def run(files):
        exercise = workshop.exercise(DESCRIPTION, VISIBLE, HIDDEN, COMPLETE)
        return verify(exercise, workshop.submit(COMPLETE | files))

    return run


def results(verdict):
    return [report.ok for report in verdict.visible + verdict.hidden]


def reason(verdict):
    assert verdict.status is Status.FAILED and verdict.admissibility == []
    (problem,) = verdict.absent
    return f"{problem.location} {problem.message}".strip()


def display(verdict):
    console = Console(file=io.StringIO(), width=160)
    show_verdict(console, verdict)
    return console.file.getvalue()


def test_complete_code(check):
    verdict = check({})
    assert verdict.status is Status.PASSED and verdict.absent == []


def test_missing_function_fails_its_own_tests_only(check):
    verdict = check({"tables/calculs.py": SOLUTION})
    assert reason(verdict) == "tables/calculs.py fonction doubler absente de tables/calculs.py"
    assert results(verdict) == [True, False, True, True, False]
    text = display(verdict)
    assert "TESTS RATÉS" in text and "fonction doubler absente" in text
    assert "1 raté(s) sur 2 : fonction absente ou signature différente" in text
    assert "654" not in text and "987" not in text


def test_constraints_on_a_missing_function_are_not_reported(check):
    assert check({"tables/calculs.py": SOLUTION}).constraints == []


def test_empty_files_are_admissible(check):
    verdict = check(dict.fromkeys(COMPLETE, ""))
    assert verdict.status is Status.FAILED and verdict.admissibility == []
    assert len(verdict.absent) == 3 and not any(results(verdict))


@pytest.mark.parametrize(
    ("header", "expected"),
    [
        ("table(valeur, taille=3)", "(nombre, taille=3), tu as (valeur, taille=3)"),
        ("table(taille=3, nombre=2)", "(taille=3, nombre=2)"),
        ("table(nombre)", "tu as (nombre)"),
        ("table(nombre, taille)", "tu as (nombre, taille)"),
        ("table(nombre, taille=4)", "taille=4"),
        ("table(nombre, taille=3, autre=1)", "autre=1"),
        ("table(*nombres)", "*nombres"),
        ("tabel(nombre, taille=3)", "tu as défini tabel"),
        ("Table(nombre, taille=3)", "absente"),
    ],
)
def test_signatures(check, header, expected):
    code = f"def {header}:\n    return []\n{DOUBLER}"
    main = "def main():\n    print([2, 4, 6])\n\n\nif __name__ == '__main__':\n    main()\n"
    verdict = check({"tables/calculs.py": code, "main.py": main})
    assert expected in reason(verdict)
    assert results(verdict) == [False, True, True, False, True]


def test_annotations_are_free(check):
    code = SOLUTION.replace("nombre: int, taille: int = 3) -> list[int]", "nombre, taille=3)")
    assert check({"tables/calculs.py": code + DOUBLER}).passed


def test_function_in_the_wrong_file(check):
    main = MAIN.replace("from tables.calculs import table\n", "") + SOLUTION
    verdict = check({"tables/calculs.py": DOUBLER, "main.py": main})
    assert "tu l'as définie dans main.py" in reason(verdict)


def test_nested_function(check):
    code = "def autre():\n    def table(nombre, taille=3):\n        return []\n    return table\n"
    main = "def main():\n    print([2, 4, 6])\n\n\nmain()\n"
    verdict = check({"tables/calculs.py": code + DOUBLER, "main.py": main})
    assert "ligne 2" in reason(verdict) and "imbriquée" in reason(verdict)


def test_main_function(check):
    verdict = check({"main.py": "print('a')\n"})
    assert "main() absente" in reason(verdict)
    assert results(verdict) == [True, True, False, True, True]
    assert "paramètre" in reason(check({"main.py": "def main(nombre):\n    print(nombre)\n"}))
