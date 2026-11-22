import pytest

from prb import cli
from prb.bank import load_exercise
from prb.model import BankError
from prb.validation import statement_examples, validate_exercise
from tests.conftest import FUNCTION, HIDDEN, SOLUTION

STATEMENT = "tables.py table\n\n```\n>>> table(2)\n[2, 4, 6]\n```\n"
MANY = HIDDEN.replace('"table(0)"', ", ".join(f'"table({n})"' for n in range(8, 14)))


@pytest.fixture
def validate(workshop):
    def run(statement=STATEMENT, hints="indices = ['a', 'b']", **options):
        workshop.exercise(**{"hidden": MANY, **options})
        workshop.write(workshop.paths.exercises / "demo", {"enonce.md": statement})
        workshop.write(workshop.paths.private / "demo", {"indices.toml": hints})
        return validate_exercise(workshop.paths, "demo")

    return run


def test_a_complete_exercise_is_valid(validate):
    result = validate()
    assert result.problems == []
    assert (result.visible, result.hidden, result.hints) == (2, 7, 2)


@pytest.mark.parametrize(
    ("solution", "expected"),
    [
        (SOLUTION.replace("range(1", "inconnu(1"), "échoue"),
        (SOLUTION.replace("taille + 1", "taille"), "2 test(s) visible(s)"),
        (SOLUTION.replace(":return:", ":retour:"), "qualité"),
        (SOLUTION.replace("return [", "return [0] + ["), "rate 2"),
    ],
)
def test_bad_solutions(validate, solution, expected):
    problems = validate(solution={"tables.py": solution}).problems
    assert any(expected in problem for problem in problems) or "non recevable" in problems[0]


def test_solution_that_ignores_its_constraints(validate):
    description = f'{FUNCTION}\n[contraintes]\ninterdits = ["compréhension"]\n'
    problems = validate(STATEMENT + " compréhension", description=description).problems
    assert any("contrainte non respectée" in problem for problem in problems)


def test_slow_solution(validate):
    description = FUNCTION.replace('"fonction"', '"fonction"\ntimeout_secondes = 1.0')
    slow = SOLUTION.replace('    return', '    time.sleep(0.6 if nombre == 5 else 0)\n    return')
    slow = slow.replace('"""Tables de multiplication."""', '"""Tables."""\n\nimport time')
    problems = validate(description=description, solution={"tables.py": slow}).problems
    assert problems == ["la solution met plus de 0.5 s sur un test"]


@pytest.mark.parametrize(
    ("options", "expected"),
    [
        ({"hidden": HIDDEN}, "moins de 6 tests cachés"),
        ({"hidden": MANY.replace("table(8)", "table(9)")}, "en double"),
        ({"hidden": MANY.replace("table(8)", "table(2)")}, "identique"),
        ({"hints": "indices = ['a']"}, "2 ou 3 indices"),
        ({"statement": STATEMENT.replace("6]", "7]")}, "exemple faux dans l'énoncé : table(2)"),
        ({"statement": "tables.py table"}, "aucun exemple"),
        ({"statement": "Tables.py"}, "« table »"),
        ({"statement": "table"}, "« tables.py »"),
        ({"solution": {"tables.py": SOLUTION, "trop.py": ""}}, "trop.py"),
    ],
)
def test_incomplete_exercises(validate, options, expected):
    problems = validate(**options).problems
    assert any(expected in problem for problem in problems), problems


def test_statement_must_announce_the_constraints(validate):
    description = f'{FUNCTION}\n[contraintes]\ninterdits = ["lambda"]\n'
    problems = validate(description=description).problems
    assert problems == ["l'énoncé ne mentionne pas « lambda »"]


def test_examples_of_the_statement(workshop, validate):
    text = (
        "tables.py table\n```\n>>> table(2)\n[2,\n 4, 6]\n>>> autre(3)\n1\n>>> table(5, taille=2)\n"
        "[5, 10]\n```\n>>> nombre = 3\n>>> table(1, 2)\n1\n2\n"
    )
    validate(text)
    examples = statement_examples(load_exercise(workshop.paths, "demo"))
    assert [(case.label, case.has_value) for case in examples] == [
        ("table(2)", True),
        ("table(5, taille=2)", True),
        ("table(1, 2)", False),
    ]
    assert examples[0].value == [2, 4, 6] and examples[2].output == "1\n2"


@pytest.mark.parametrize("call", ["secret(123)", "table(secret)", "table(123"])
def test_hidden_tests_are_not_revealed_by_a_format_error(workshop, call):
    with pytest.raises(BankError) as error:
        workshop.exercise(hidden=MANY.replace("table(8)", call))
    assert "tests_caches" in str(error.value)
    assert "secret" not in str(error.value) and "123" not in str(error.value)


def test_command(workshop, validate, capsys, monkeypatch):
    monkeypatch.setenv("COLUMNS", "120")
    validate()
    assert cli.main(["valider"], workshop.paths) == 0
    output = capsys.readouterr().out
    assert "✓ demo" in output and "1/1 exercices valides" in output
    (workshop.paths.private / "orphelin").mkdir()
    assert cli.main(["valider"], workshop.paths) == 1
    assert "_prive/orphelin" in capsys.readouterr().out
    assert cli.main(["valider", "demo"], workshop.paths) == 0
    assert cli.main(["valider", "absent"], workshop.paths) == 1
    assert "exercice inconnu" in capsys.readouterr().out
