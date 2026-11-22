import pytest

from prb.admissibility import check_admissibility
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
def examine(workshop):
    """Give the blocking problems and the warnings of a submission."""

    def run(files):
        exercise = workshop.exercise(PACKAGE, VISIBLE, "", GOOD)
        folder = workshop.submit(files)
        result = check_admissibility(exercise, folder, read_sources(folder))
        return tuple(
            [f"{problem.location} {problem.message}".strip() for problem in problems]
            for problems in (result.errors, result.warnings)
        )

    return run


@pytest.fixture
def check(examine):
    """Give the messages of the blocking problems of a submission."""
    return lambda files: examine(files)[0]


@pytest.fixture
def warn(examine):
    """Give the messages of the warnings of an admissible submission."""

    def run(files):
        errors, warnings = examine(files)
        assert errors == []
        return warnings

    return run


def single(messages):
    assert len(messages) == 1, messages
    return messages[0]


def test_good_submission(examine):
    assert examine(GOOD) == ([], [])


def test_missing_folder(workshop):
    exercise = workshop.exercise()
    problems = check_admissibility(exercise, workshop.student, {}).errors
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


def test_empty_files_are_accepted(examine):
    assert examine(dict.fromkeys(GOOD, "")) == ([], [])


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
    problems = check_admissibility(exercise, folder, read_sources(folder)).errors
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


@pytest.mark.parametrize(
    "body",
    [
        "    valeur = 1\n    del valeur\n    return valeur",
        "    try:\n        pass\n    except OSError as valeur:\n        pass\n    return valeur",
    ],
)
def test_names_that_may_be_undefined_are_warnings(warn, body):
    code = f"def table(nombre, taille=3):\n{body}\n"
    assert "« valeur » peut ne pas" in single(warn(GOOD | {"tables/calculs.py": code}))


def test_annotations_between_quotes_are_warnings(warn, check):
    code = "def table(nombre: 'Entier', taille=3):\n    return []\n"
    assert "« Entier »" in single(warn(GOOD | {"tables/calculs.py": code}))
    assert "« Entier »" in single(check(GOOD | {"tables/calculs.py": code.replace("'", "")}))


def test_return_inside_finally(check):
    code = "def table(nombre, taille=3):\n    try:\n        pass\n    finally:\n        return []\n"
    assert "« return » interdit" in single(check(GOOD | {"tables/calculs.py": code}))


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
        ("from . import calculs", "« calculs » n'existe pas dans la racine"),
        ("from .calculs import table", "« calculs » introuvable"),
        ("from .. import calculs", "import relatif impossible"),
        ("from tables.calculs import ESSAI", "« ESSAI » n'existe pas"),
        ("from tables.calculs import *\nprint(tabel(2))", "nom « tabel » non défini"),
        ("from tables.calculs import *\nprint(_PRIVE)", "nom « _PRIVE » non défini"),
        ("from math import *\nprint(racine(2))", "nom « racine » non défini"),
        ("from tables import *\nprint(calculs)", "nom « calculs » non défini"),
    ],
)
def test_broken_imports(check, line, expected):
    calculs = f"_PRIVE = 1\n\n{SOLUTION}\n\nif __name__ == '__main__':\n    ESSAI = table(2)\n"
    files = GOOD | {"tables/calculs.py": calculs, "main.py": f"{line}\n"}
    assert expected in single(check(files))


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("import tables.calculs\ntables.calculs.tabel(2)", "« tabel » n'existe pas"),
        ("from tables import calculs\ncalculs.tabel(2)", "« tabel » n'existe pas"),
        ("from tables import calculs as outils\noutils.tabel(2)", "« tabel » n'existe pas"),
        ("import math\nmath.racine(2)", "« racine » n'existe pas"),
        ("from . import tables", "import relatif à la racine"),
        ("from .tables.calculs import table", "import relatif à la racine"),
    ],
)
def test_suspicious_imports(warn, line, expected):
    assert expected in single(warn(GOOD | {"main.py": f"{line}\n"}))


def test_imports_between_modules_of_a_package(warn):
    files = GOOD | {"tables/outils.py": "def double(nombre):\n    return nombre * 2\n"}
    expected = {
        "from tables.outils import double": None,
        "from .outils import double": None,
        "from outils import double": "écris « tables.outils »",
        "import outils": "écris « tables.outils »",
        "from ..main import main": "import relatif à la racine",
    }
    for line, message in expected.items():
        found = warn(files | {"tables/calculs.py": f"{line}\n\n\n{SOLUTION}"})
        found.remove(
            "tables/outils.py fichier non prévu par l'énoncé : retire-le avant de créer le ZIP"
        )
        assert (found == []) if message is None else (message in single(found))


@pytest.mark.parametrize("error", ["ImportError", "(OSError, ImportError)", "ValueError"])
def test_guarded_imports_are_ignored(examine, error):
    code = f"try:\n    import rich\nexcept {error}:\n    rich = None\n"
    assert examine(GOOD | {"main.py": code}) == ([], [])


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
        "from tables.calculs import *\nprint(table(2))",
        "from math import *\nprint(sqrt(2))",
        "from tables import __init__",
    ],
)
def test_correct_imports(examine, line):
    code = f"{line}\n\n\ndef main():\n    pass\n"
    assert examine(GOOD | {"main.py": code}) == ([], [])


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


def test_extra_files_are_only_warnings(warn):
    extra = {"brouillon.py": "", "notes.txt": "", "__pycache__/x.py": "", ".idea/y.py": ""}
    assert warn(GOOD | extra) == [
        "brouillon.py fichier non prévu par l'énoncé : retire-le avant de créer le ZIP"
    ]
