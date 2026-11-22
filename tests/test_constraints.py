import ast

import pytest

from prb.constraints import check_constraints
from prb.constructs import CONSTRUCTS
from prb.sources import read_sources
from tests.conftest import FUNCTION

# One example of each construct, and code that looks like it but is allowed.
EXAMPLES = {
    "break": ("for x in a:\n    break", "broken = 1"),
    "continue": ("for x in a:\n    continue", "suite = 'continue'"),
    "try": ("try:\n    a\nexcept ValueError:\n    b", "raise ValueError"),
    "while True": ("while True:\n    a()", "while a:\n    a()"),
    "while": ("while a:\n    a()", "for x in a:\n    b()"),
    "for": ("for x in a:\n    b()", "[x for x in a]"),
    "if": ("if a:\n    b()", "a if b else c"),
    "match": ("match a:\n    case 1:\n        b()", "match = 1"),
    "with": ("with a:\n    b()", "a()"),
    "lambda": ("f = lambda x: x", "def f(x):\n    return x"),
    "global": ("def f():\n    global a\n    a = 1", "a = 1"),
    "ternaire": ("a if b else c", "if a:\n    b()"),
    "compréhension": ("{x: 1 for x in a}", "for x in a:\n    b()"),
    "tranche": ("a[1:]", "a[1]"),
    "f-string": ("f'{a}'", "'{a}'"),
    "dictionnaire": ("{1: 2}", "{1, 2}"),
    "ensemble": ("{1, 2}", "{1: 2}"),
    "liste": ("[1, 2]", "[a, b] = 1, 2"),
}


@pytest.mark.parametrize("name", CONSTRUCTS)
def test_each_construct(name):
    yes, no = EXAMPLES[name]
    assert any(CONSTRUCTS[name](node) for node in ast.walk(ast.parse(yes)))
    assert not any(CONSTRUCTS[name](node) for node in ast.walk(ast.parse(no)))


@pytest.mark.parametrize("test", ["True", "1", "'a'", "not False", "not not True", "not 0"])
def test_disguised_while_true(test):
    assert any(CONSTRUCTS["while True"](n) for n in ast.walk(ast.parse(f"while {test}: pass")))


@pytest.mark.parametrize("test", ["False", "not True", "a", "not a", "a == True"])
def test_ordinary_while(test):
    assert not any(CONSTRUCTS["while True"](n) for n in ast.walk(ast.parse(f"while {test}: pass")))


@pytest.fixture
def check(workshop):
    def run(constraints, body, before=""):
        exercise = workshop.exercise(f"{FUNCTION}\n{constraints}\n")
        code = f"{before}\n\ndef table(nombre, taille=3):\n"
        code += "".join(f"    {line}\n" for line in body.splitlines())
        folder = workshop.submit(code)
        return [problem.message for problem in check_constraints(exercise, read_sources(folder))]

    return run


def test_forbidden_construct_gives_its_line(workshop):
    exercise = workshop.exercise(f'{FUNCTION}\n[contraintes]\ninterdits = ["break"]\n')
    folder = workshop.submit("def table(nombre, taille=3):\n    for x in []:\n        break\n")
    (problem,) = check_constraints(exercise, read_sources(folder))
    assert (problem.file, problem.line, problem.source) == ("tables.py", 3, "break")


def test_required_construct(check):
    rule = '[contraintes]\nimposes = ["while"]'
    assert check(rule, "while nombre:\n    nombre -= 1") == []
    assert check(rule, "return []") == ["l'énoncé impose d'utiliser « while »"]


@pytest.mark.parametrize(
    "body",
    [
        "return int('3')",
        "return list(map(int, '12'))",
        "entier = int\nreturn entier('3')",
        "return sorted('12', key=int)",
        "import builtins\nreturn builtins.int('3')",
    ],
)
def test_forbidden_function(check, body):
    messages = check('[contraintes]\nfonctions_interdites = ["int"]', body)
    assert messages == ["int() est interdit"]


@pytest.mark.parametrize(
    "body",
    [
        "valeur: int = 3\nreturn valeur",
        "return isinstance(nombre, int)",
        "def aide(x: int) -> int:\n    return x\nreturn aide(nombre)",
        "texte = 'int(3)'\nreturn texte",
        "return nombre.int",
    ],
)
def test_the_type_int_is_not_the_function(check, body):
    assert check('[contraintes]\nfonctions_interdites = ["int"]', body) == []


def test_annotations_of_the_header_are_allowed(workshop):
    exercise = workshop.exercise(f'{FUNCTION}\n[contraintes]\nfonctions_interdites = ["int"]\n')
    header = "def table(nombre: int, taille: int = 3) -> list[int]:\n"
    folder = workshop.submit(f"{header}    return []\n")
    assert check_constraints(exercise, read_sources(folder)) == []


def test_forbidden_method(check):
    rule = '[contraintes]\nfonctions_interdites = [".replace"]'
    assert check(rule, "return 'a'.replace('a', 'b')") == ["la méthode .replace() est interdit"]
    assert check(rule, "replace = 3\nreturn replace") == []


@pytest.mark.parametrize(
    "line", ["import re", "from re import sub", "import re as r", "import re.sub"]
)
def test_forbidden_module(check, line):
    rule = '[contraintes]\nmodules_interdits = ["re"]'
    assert check(rule, "return []", before=line) == ["le module re est interdit"]
    assert check(rule, "return []", before="import random") == []


@pytest.mark.parametrize(
    "line", ["import re", "import re as motifs", "from re import search", "import random, re"]
)
def test_required_module(check, line):
    rule = '[contraintes]\nmodules_imposes = ["re"]'
    assert check(rule, "return []", line) == []
    assert check(rule, f"{line}\nreturn []") == []
    message = "l'énoncé impose d'utiliser le module re"
    assert check(rule, "return []", "import random\nfrom random import choice") == [message]


def test_required_call(check):
    rule = '[contraintes]\nappels_imposes = ["aide"]'
    aide = "def aide(x):\n    return x\n"
    assert check(rule, "return aide(3)", before=aide) == []
    assert check(rule, "return list(map(aide, []))", before=aide) == []
    assert len(check(rule, "return []", before=aide)) == 1


def test_a_recursive_call_does_not_count(check):
    rule = '[contraintes]\nappels_imposes = ["aide"]'
    aide = "def aide(x):\n    return aide(x)\n"
    assert len(check(rule, "return []", before=aide)) == 1


def test_constraint_on_a_missing_function(workshop):
    exercise = workshop.exercise(f'{FUNCTION}\n[contraintes.fonctions.table]\nimposes = ["for"]\n')
    folder = workshop.submit("def autre():\n    pass\n")
    assert check_constraints(exercise, read_sources(folder)) == []


def test_constraint_on_one_function(check):
    rule = '[contraintes.fonctions.table]\ninterdits = ["for"]\nimposes = ["while"]'
    loop = "def autre():\n    for x in []:\n        pass\n"
    assert check(rule, "while nombre:\n    nombre -= 1", before=loop) == []
    messages = check(rule, "for x in []:\n    pass", before=loop)
    assert messages == [
        "« for » est interdit dans table",
        "l'énoncé impose d'utiliser « while » dans table",
    ]
