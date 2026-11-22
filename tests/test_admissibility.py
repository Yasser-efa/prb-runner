import pytest

from prb.admissibility import check_admissibility, unexpected_files
from prb.sources import read_sources
from tests.conftest import SOLUTION

PACKAGE = '''titre = "Package"
reference = "test"
sorte = "programme"

[organisation]
fichiers = ["main.py", "tables/__init__.py", "tables/calculs.py"]
main = "main.py"

[[fonctions]]
module = "tables.calculs"
signature = "table(nombre: int, taille: int = 3) -> list[int]"
'''
VISIBLE = '[[tests]]\nappel = "table(2)"\nattendu = "[2, 4, 6]"\n'
MAIN = (
    "from tables.calculs import table\n\n\ndef main():\n    print(table(2))\n\n\n"
    "if __name__ == '__main__':\n    main()\n"
)
GOOD = {"main.py": MAIN, "tables/__init__.py": "", "tables/calculs.py": SOLUTION}


@pytest.fixture
def check(workshop):
    """Give the messages of the blocking problems of a submission."""

    def run(files, description=PACKAGE, visible=VISIBLE):
        exercise = workshop.exercise(description, visible, "", GOOD)
        folder = workshop.submit(files)
        problems = check_admissibility(exercise, folder, read_sources(folder))
        return [f"{problem.location} {problem.message}".strip() for problem in problems]

    return run


def single(messages):
    assert len(messages) == 1, messages
    return messages[0]


def test_good_submission(check):
    assert check(GOOD) == []


def test_missing_folder(workshop):
    exercise = workshop.exercise()
    problems = check_admissibility(exercise, workshop.student, {})
    assert "mes_solutions/demo/ est vide" in problems[0].message


def test_missing_file(check):
    files = {name: text for name, text in GOOD.items() if name != "main.py"}
    assert "fichier manquant : main.py" in single(check(files))


def test_missing_init(check):
    files = {name: text for name, text in GOOD.items() if "__init__" not in name}
    assert "« tables » doit être un package" in single(check(files))


def test_wrong_case_is_refused_even_on_windows(check):
    files = {name: text for name, text in GOOD.items() if name != "main.py"}
    files["Main.py"] = MAIN
    assert "majuscules comprises" in single(check(files))


def test_wrong_case_of_a_folder(check):
    files = {
        "main.py": MAIN.replace("tables.calculs", "Tables.calculs"),
        "Tables/__init__.py": "",
        "Tables/calculs.py": SOLUTION,
    }
    messages = check(files)
    assert len(messages) == 2 and all("majuscules comprises" in text for text in messages)


def test_misplaced_file(check):
    main = MAIN.replace("tables.", "")
    files = {"main.py": main, "tables/__init__.py": "", "calculs.py": SOLUTION}
    assert "mal placé" in single(check(files))


def test_close_name_is_suggested(check):
    files = {
        "main.py": MAIN.replace("calculs", "calcul"),
        "tables/__init__.py": "",
        "tables/calcul.py": SOLUTION,
    }
    assert "tu as « tables/calcul.py »" in single(check(files))


def test_empty_required_file_is_accepted_but_function_is_missing(check):
    messages = check(GOOD | {"tables/calculs.py": "", "main.py": "def main():\n    pass\n"})
    assert "fonction table absente" in single(messages)


@pytest.mark.parametrize(
    ("code", "line"),
    [
        ("def f(a:\n    return a\n", 1),
        ("if True\n    pass\n", 1),
        ("def f():\n    pass\n  x = 1\n", 3),
        ("return 3\n", 1),
        ("def f():\n    break\n", 2),
        ("f() = 3\n", 1),
        ("def f(a, a):\n    pass\n", 1),
        ("x = 'abc\n", 1),
    ],
)
def test_syntax_errors(check, code, line):
    messages = check(GOOD | {"main.py": code})
    assert f"main.py, ligne {line}" in messages[0] and "Error" in messages[0]


def test_badly_encoded_file(workshop):
    exercise = workshop.exercise(PACKAGE, VISIBLE, "", GOOD)
    folder = workshop.submit(GOOD)
    (folder / "main.py").write_bytes("# é".encode("latin-1"))
    problems = check_admissibility(exercise, folder, read_sources(folder))
    assert "UTF-8" in problems[0].message


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        ("    return inconnu", "nom « inconnu » non défini"),
        ("    total += nombre\n    return total", "total"),
        ("    print(valeur)\n    valeur = 3\n    return valeur", "valeur"),
    ],
)
def test_undefined_names(check, body, expected):
    code = f"def table(nombre, taille=3):\n{body}\n"
    assert expected in single(check(GOOD | {"tables/calculs.py": code}))


def test_noqa_does_not_hide_an_error(check):
    code = "def table(nombre, taille=3):\n    return inconnu  # noqa\n"
    assert "inconnu" in single(check(GOOD | {"tables/calculs.py": code}))


def test_unused_names_are_not_blocking(check):
    code = "import math\n\n\ndef table(nombre, taille=3):\n    reste = 3\n    return []\n"
    assert check(GOOD | {"tables/calculs.py": code}) == []


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("import rich", "introuvable"),
        ("import module_inexistant", "introuvable"),
        ("from tables import absent", "« absent » n'existe pas"),
        ("from tables.calculs import tabel", "« tabel » n'existe pas"),
        ("import tables.calcul", "« tables.calcul » n'existe pas"),
        ("from calculs import table", "il s'appelle « tables.calculs »"),
        ("from math import racine", "« racine » n'existe pas"),
        ("import os.chemin", "« os.chemin » n'existe pas"),
        ("from . import calculs", "import relatif impossible"),
        ("from .. import calculs", "import relatif impossible"),
        ("import tables.calculs\ntables.calculs.tabel(2)", "« tabel » n'existe pas"),
        ("from tables import calculs\ncalculs.tabel(2)", "« tabel » n'existe pas"),
        ("from tables import calculs as outils\noutils.tabel(2)", "« tabel » n'existe pas"),
        ("import math\nmath.racine(2)", "« racine » n'existe pas"),
    ],
)
def test_broken_imports(check, line, expected):
    code = f"{line}\n\n\ndef main():\n    pass\n"
    assert expected in single(check(GOOD | {"main.py": code}))


@pytest.mark.parametrize(
    "line",
    [
        "import tables",
        "import tables.calculs\ntables.calculs.table(2)",
        "from tables import calculs\ncalculs.table(2)",
        "from tables.calculs import table",
        "from tables.calculs import *",
        "import math\nmath.pi.hex()",
        "import os.path\nos.path.join('a')",
        "from collections import Counter\nCounter.fromkeys('a')",
        "import random as hasard\nhasard.randint(1, 2)",
        "import math\n\n\ndef aide(math):\n    return math.racine",
    ],
)
def test_correct_imports(check, line):
    assert check(GOOD | {"main.py": f"{line}\n\n\ndef main():\n    pass\n"}) == []


def test_relative_import_inside_a_package(check):
    files = GOOD | {
        "tables/calculs.py": "from .outils import double\n\n\n"
        "def table(nombre, taille=3):\n    return double(nombre)\n",
        "tables/outils.py": "def double(nombre):\n    return nombre * 2\n",
    }
    assert check(files) == []
    files["tables/outils.py"] = "def triple(nombre):\n    return nombre * 3\n"
    assert "« double » n'existe pas" in single(check(files))


def test_names_defined_in_branches_count(check):
    code = (
        "import sys\n\nif sys.argv:\n    LIMITE = 3\nelse:\n    LIMITE, AUTRE = 4, 5\n"
        "for nombre in range(3):\n    pass\n\n\ndef table(nombre, taille=3):\n    return []\n"
    )
    main = "from tables.calculs import AUTRE, LIMITE, nombre\n\n\ndef main():\n    pass\n"
    assert check(GOOD | {"tables/calculs.py": code, "main.py": main}) == []


@pytest.mark.parametrize(
    ("header", "expected"),
    [
        ("table(valeur, taille=3)", "(valeur, taille=3)"),
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
    code = f"def {header}:\n    return []\n"
    main = "def main():\n    pass\n"
    assert expected in single(check(GOOD | {"tables/calculs.py": code, "main.py": main}))


def test_annotations_are_free(check):
    code = "def table(nombre: float, taille: 'int' = 3):\n    return []\n"
    assert check(GOOD | {"tables/calculs.py": code}) == []


def test_function_in_the_wrong_file(check):
    files = GOOD | {"tables/calculs.py": "", "main.py": SOLUTION + "\n\ndef main():\n    pass\n"}
    assert "tu l'as définie dans main.py" in single(check(files))


def test_nested_function(check):
    code = "def autre():\n    def table(nombre, taille=3):\n        return []\n    return table\n"
    main = "def main():\n    pass\n"
    assert "imbriquée" in single(check(GOOD | {"tables/calculs.py": code, "main.py": main}))


def test_main_function(check):
    assert "main() absente" in single(check(GOOD | {"main.py": "print('a')\n"}))
    with_parameter = "def main(nombre):\n    print(nombre)\n"
    assert "paramètre" in single(check(GOOD | {"main.py": with_parameter}))


def test_extra_files_are_only_reported(workshop):
    exercise = workshop.exercise(PACKAGE, VISIBLE, "", GOOD)
    extra = {"brouillon.py": "", "notes.txt": "", "__pycache__/x.py": "", ".idea/y.py": ""}
    folder = workshop.submit(GOOD | extra)
    assert check_admissibility(exercise, folder, read_sources(folder)) == []
    assert [problem.file for problem in unexpected_files(exercise, folder)] == ["brouillon.py"]
