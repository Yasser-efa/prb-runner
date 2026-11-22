import pytest

from prb.quality import GROUPS, check_quality
from prb.sources import read_sources
from tests.conftest import FUNCTION, SOLUTION

MAIN = FUNCTION.replace('["tables.py"]', '["tables.py", "main.py"]\nmain = "main.py"')
DOC = '''    """
    Calcule.

    :param nombre: un
    :param taille: deux
    :return: trois
    """
'''
HEADER = "def table(nombre: int, taille: int = 3) -> list[int]:\n"


@pytest.fixture
def remarks(workshop):
    def run(files, description=FUNCTION):
        exercise = workshop.exercise(description)
        folder = workshop.submit(files)
        found = check_quality(exercise, folder, read_sources(folder))
        assert all(remark.group in GROUPS for remark in found)
        return [remark.message for remark in found]

    return run


def test_clean_code(remarks):
    assert remarks(SOLUTION) == []


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        (SOLUTION.replace("nombre * rang", "nombre*rang + 1").replace("= 3", "=3"), "E252"),
        (SOLUTION.replace("(1, taille", "(1,taille"), "après « , »"),
        (SOLUTION.replace('"""\n\n\ndef', '"""\n\ndef'), "2 lignes vides"),
        (SOLUTION.rstrip("\n"), "retour à la ligne à la fin"),
        (SOLUTION.replace("rang for", "rang  for"), "plusieurs espaces"),
        (SOLUTION + "x = 1 \n", "espaces en fin de ligne"),
        (SOLUTION + "\n\nTEXTE = '" + "a" * 130 + "'\n", "caractères, 120 au maximum"),
        (SOLUTION + "\n\ndef MaFonction():\n    pass\n", "en_minuscules"),
        (SOLUTION + "\nlist = 3\n", "écrase une fonction prédéfinie"),
        ("import math\n\n" + SOLUTION, "import inutilisé (math)"),
    ],
)
def test_style(remarks, code, expected):
    found = remarks(code)
    if expected == "E252":
        expected = "autour du = d'un paramètre annoté"
    assert any(expected in message for message in found), found


def test_spacing_around_products_is_free(remarks):
    assert remarks(SOLUTION.replace("nombre * rang", "nombre*rang + 1")) == []


def test_messages_are_in_french(remarks):
    code = "import os\ndef f(X):\n    Y=X+1\n    return Y\nprint( f(1) )\nif f == None:\n    pass\n"
    english = ("Missing", "Expected", "imported but unused", "Whitespace", "Comparison")
    assert not [message for message in remarks(code) if message.startswith(english)]


@pytest.mark.parametrize(
    ("docstring", "expected"),
    [
        ("", "docstring absente"),
        (DOC.replace("    Calcule.\n\n", ""), "description absente"),
        (DOC.replace("    :param taille: deux\n", ""), "« :param taille: » absent"),
        (DOC.replace("taille: deux", "taille:"), "« :param taille: » sans description"),
        (DOC.replace("    :return: trois\n", ""), "« :return: » absent"),
        (DOC.replace(":return: trois", ":return:"), "« :return: » sans description"),
        (DOC.replace("taille: deux", "autre: deux"), "« autre » est documenté"),
        (DOC.replace(":param taille:", ":parametre taille:"), "étiquette Sphinx inconnue"),
    ],
)
def test_docstrings(remarks, docstring, expected):
    found = remarks(f"{HEADER}{docstring}    return [nombre] * taille\n")
    assert any(expected in message for message in found), found


def test_types_without_annotations(remarks):
    header = "def table(nombre, taille=3):\n"
    found = remarks(f"{header}{DOC}    return [nombre] * taille\n")
    assert {message for message in found if "type" in message} == {
        "table : type de « nombre » absent (annotation ou :type nombre:)",
        "table : type de « taille » absent (annotation ou :type taille:)",
        "table : type de la valeur renvoyée absent (annotation -> ou :rtype:)",
    }


def test_types_in_the_docstring(remarks):
    header = "def table(nombre, taille=3):\n"
    doc = DOC.replace("    :return:", "    :type nombre: int\n    :type taille: int\n    :return:")
    doc = doc.replace("trois\n", "trois\n    :rtype: list[int]\n")
    assert remarks(f"{header}{doc}    return [nombre] * taille\n") == []
    doc = DOC.replace("param ", "param int ")
    doc = doc.replace("trois\n", "trois\n    :rtype: list[int]\n")
    assert remarks(f"{header}{doc}    return [nombre] * taille\n") == []


def test_description_on_several_lines(remarks):
    doc = DOC.replace(":return: trois", ":return:\n        trois\n        suite")
    assert remarks(f"{HEADER}{doc}    return [nombre] * taille\n") == []


def test_function_without_return_needs_no_return_tag(remarks):
    code = SOLUTION + '\n\ndef afficher() -> None:\n    """Affiche."""\n    print("a")\n'
    assert remarks(code) == []


def test_single_letter_names(remarks):
    code = SOLUTION.replace("rang", "r")
    assert remarks(code) == ["nom d'une seule lettre « r » dans table"]
    code = SOLUTION + "\n\nfor _ in range(3):\n    pass\n"
    assert remarks(code) == []


def loop(body):
    return f"{HEADER}{DOC}" + "".join(f"    {line}\n" for line in body.splitlines())


@pytest.mark.parametrize(
    "body",
    [
        "for rang in range(3):\n    pass\nreturn [rang]",
        "for rang in range(3):\n    pass\nrang += 1\nreturn []",
        "for rang in range(3):\n    pass\nprint([x1 for x1 in range(rang)])\nreturn []",
        "for rang, autre in enumerate('ab'):\n    pass\nif nombre:\n    print(autre)\nreturn []",
        "for rang in range(3):\n    for rang in range(2):\n        pass\nreturn []",
        "for rang in range(3):\n    pass\nfor rang in range(rang):\n    pass\nreturn []",
    ],
)
def test_loop_variable_used_after_the_loop(remarks, body):
    assert any("variable de boucle" in message for message in remarks(loop(body)))


@pytest.mark.parametrize(
    "body",
    [
        "for rang in range(3):\n    print(rang)\nreturn []",
        "for rang in range(3):\n    pass\nrang = 4\nreturn [rang]",
        "for rang in range(3):\n    pass\nfor rang in range(4):\n    print(rang)\nreturn []",
        "for rang in range(3):\n    pass\nreturn [rang for rang in range(2)]",
        "if nombre:\n    for rang in range(3):\n        pass\nelse:\n    rang = 1\nreturn []",
        "for _ in range(3):\n    for _ in range(2):\n        pass\nreturn []",
        "for rang in range(3):\n    if rang:\n        return [rang]\nreturn []",
    ],
)
def test_correct_loops(remarks, body):
    assert not any("variable de boucle" in message for message in remarks(loop(body)))


def test_loop_variable_in_the_other_branch(remarks):
    body = "rang = 0\nif nombre:\n    for rang in range(3):\n        pass\n"
    body += "else:\n    print(rang)\nreturn []"
    assert not any("variable de boucle" in message for message in remarks(loop(body)))


@pytest.mark.parametrize(
    ("ending", "ok"),
    [
        ("if __name__ == '__main__':\n    main()\n", True),
        ('if "__main__" == __name__:\n    main()\n', True),
        ("main()\n", False),
        ("if __name__ != '__main__':\n    main()\n", False),
    ],
)
def test_main_guard(remarks, ending, ok):
    main = f'def main() -> None:\n    """Lance le programme."""\n    print("a")\n\n\n{ending}'
    found = remarks({"tables.py": SOLUTION, "main.py": main}, MAIN)
    assert any("__main__" in message for message in found) is not ok


def test_extra_file(remarks):
    found = remarks({"tables.py": SOLUTION, "brouillon.py": ""})
    assert found == ["fichier non demandé : retire-le avant de créer le ZIP"]
