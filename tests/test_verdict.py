import io
import shutil
from datetime import datetime

import pytest
from rich.console import Console

from prb import cli, pycharm
from prb.bank import load_bank, load_exercise
from prb.model import BankError
from prb.progress import Progress
from prb.report import show_verdict
from prb.verdict import Status, verify
from tests.conftest import FUNCTION, SOLUTION


@pytest.fixture
def check(workshop):
    def run(code, **options):
        exercise = workshop.exercise(**options)
        return verify(exercise, workshop.submit(code))

    return run


def display(verdict):
    console = Console(file=io.StringIO(), width=160)
    show_verdict(console, verdict, "tentative n° 1")
    return console.file.getvalue()


def test_correct_code_passes(check):
    verdict = check(SOLUTION)
    assert verdict.status is Status.PASSED and verdict.remarks == []
    assert len(verdict.visible) == 2 and len(verdict.hidden) == 2
    text = display(verdict)
    assert "RÉUSSI" in text and "tentative n° 1" in text and "Tests cachés : 2/2" in text


def test_visible_tests_show_call_expected_and_obtained(check):
    verdict = check("def table(nombre, taille=3):\n    return [2, 4, 7]\n")
    text = display(verdict)
    assert verdict.status is Status.FAILED
    for part in ("table(2)", "[2, 4, 6]", "[2, 4, 7]", "✗", "TESTS RATÉS"):
        assert part in text


def test_hidden_values_are_never_shown(check):
    hidden = '[[groupes]]\ntheme = "secret"\nappels = ["table(987654)"]\n'
    wrong = SOLUTION.replace("return [", "return [0] if nombre > 9 else [")
    text = display(check(wrong, hidden=hidden))
    assert "987654" not in text and "1975308" not in text
    assert "secret" in text and "1 raté(s) sur 1 : mauvais résultat" in text


def test_message_of_a_hidden_exception_is_not_shown(check):
    hidden = '[[groupes]]\ntheme = "secret"\nappels = ["table(987654)"]\n'
    check_first = "    if nombre > 9:\n        raise KeyError(nombre)\n    return"
    code = SOLUTION.replace("    return", check_first)
    text = display(check(code, hidden=hidden))
    assert "987654" not in text and "KeyError (tables.py, ligne" in text


def test_all_or_nothing(check):
    wrong = SOLUTION.replace("return [", "return [1] if nombre == 0 else [")
    verdict = check(wrong)
    assert all(report.ok for report in verdict.visible)
    assert verdict.status is Status.FAILED


def test_a_tuple_is_not_a_list(check):
    verdict = check(SOLUTION.replace("return [", "return tuple([").replace("1)]", "1)])"))
    assert verdict.status is Status.FAILED and "(type tuple)" in display(verdict)


def test_floats_are_tolerated(check):
    visible = '[[tests]]\nappel = "table(1)"\nattendu = "[0.3]"\n'
    code = "def table(nombre, taille=3):\n    return [0.1 + 0.2]\n"
    assert check(code, visible=visible, hidden="").passed


def test_inadmissible_code_is_not_run(check):
    verdict = check("def table(nombre, taille=3):\n    return inconnu\n")
    assert verdict.status is Status.NOT_ADMISSIBLE
    assert verdict.visible == [] and "NON RECEVABLE" in display(verdict)


def test_broken_constraint_does_not_hide_the_tests(check):
    description = f'{FUNCTION}\n[contraintes]\ninterdits = ["compréhension"]\n'
    verdict = check(SOLUTION, description=description)
    assert verdict.status is Status.CONSTRAINTS and verdict.tests_passed
    text = display(verdict)
    assert "CONTRAINTE NON RESPECTÉE" in text and "ET TESTS RATÉS" not in text
    verdict = check(SOLUTION.replace("[nombre *", "[2 *"), description=description)
    assert verdict.status is Status.CONSTRAINTS and not verdict.tests_passed
    assert "CONTRAINTE NON RESPECTÉE ET TESTS RATÉS" in display(verdict)


def test_warnings_do_not_block(check):
    verdict = check({"tables.py": SOLUTION, "brouillon.py": ""})
    assert verdict.passed
    assert "fichier non prévu par l'énoncé" in display(verdict)


@pytest.mark.parametrize("code", [SOLUTION, "def table(nombre, taille=3):\n    return inconnu\n"])
def test_paper_preparation_is_recalled(check, code):
    assert "phase préparatoire sur papier, à ton nom" in display(check(code))


def test_exception_display(check):
    text = display(check("def table(nombre, taille=3):\n    return [1][5]\n"))
    assert "IndexError : list index out of range" in text
    assert "tables.py, ligne 2" in text and "harness" not in text


def test_timeout_display(check):
    description = FUNCTION.replace('"fonction"', '"fonction"\ntimeout_secondes = 0.4')
    code = "def table(nombre, taille=3):\n    while taille:\n        nombre += 1\n"
    text = display(check(code, description=description))
    assert "boucle infinie ?" in text and "tables.py, ligne" in text


def test_returning_a_float_is_a_remark(check):
    visible = '[[tests]]\nappel = "table(2)"\nattendu = "[2, 4, 6]"\n'
    verdict = check(SOLUTION.replace("nombre * rang", "nombre * rang / 1"), visible=visible)
    assert verdict.passed
    assert "au lieu de 2 (int)" in verdict.remarks[0].message


def test_float_is_fine_when_the_signature_says_so(check):
    description = FUNCTION.replace("list[int]", "list[float]")
    verdict = check(SOLUTION.replace("nombre * rang", "nombre * rang / 1"), description=description)
    assert verdict.passed and verdict.remarks == []


def test_debug_prints_are_a_remark(check):
    verdict = check(SOLUTION.replace("    return", "    print(nombre)\n    return"))
    assert verdict.passed and "affiche du texte" in verdict.remarks[0].message


def test_noise_at_import_is_a_remark(check):
    verdict = check(SOLUTION + "\n\nprint(table(3))\n")
    assert verdict.passed and "quand on l'importe" in verdict.remarks[0].message


def test_functions_that_display(check):
    description = FUNCTION.replace("list[int]", "None")
    visible = '[[tests]]\nappel = "table(2, 2)"\nsortie = "2\\n4\\n"\n'
    hidden = '[[groupes]]\ntheme = "affichage"\nappels = ["table(3, 1)"]\n'
    good = "def table(nombre, taille=3):\n    print(nombre)\n    print(nombre * 2)\n"
    options = {"description": description, "visible": visible, "hidden": hidden}
    assert check(good, **options, solution={"tables.py": good}).passed
    silent = "def table(nombre, taille=3):\n    print(2)\n    print(4)\n"
    verdict = check(silent, **options, solution={"tables.py": good})
    assert [report.ok for report in verdict.visible + verdict.hidden] == [True, False]


def test_broken_reference_is_reported(check):
    with pytest.raises(BankError, match="solution de référence"):
        check(SOLUTION, solution={"tables.py": "def table(nombre, taille=3):\n    return 1 / 0\n"})


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        ('sorte = "fonction"', 'sorte = "autre"', "sorte"),
        ('titre = "Table"\n', "", "titre"),
        ("reference", "refference", "clé inconnue"),
        ('module = "tables"', 'module = "absent"', "absent.py"),
        ("table(nombre", "table nombre", "signature illisible"),
        ('["tables.py"]', '["tables.py", "random.py"]', "masque un module"),
        ('["tables.py"]', '["tables.py", "../x.py"]', "chemin invalide"),
        ('["tables.py"]', '["tables.py"]\nmain = "main.py"', "main.py"),
        ('[[fonctions]]', '[contraintes]\ninterdits = ["goto"]\n\n[[fonctions]]', "goto"),
        ('[[fonctions]]', '[contraintes.fonctions.x]\n\n[[fonctions]]', "fonction inconnue"),
        ("titre", "titre titre", "exercice.toml"),
    ],
)
def test_bad_descriptions_are_refused(workshop, old, new, message):
    with pytest.raises(BankError, match=message):
        workshop.exercise(FUNCTION.replace(old, new, 1))


@pytest.mark.parametrize(
    ("visible", "message"),
    [
        ('[[tests]]\nappel = "autre(2)"\nattendu = "1"\n', "inconnue"),
        ('[[tests]]\nappel = "table(x)"\nattendu = "1"\n', "valeurs simples"),
        ('[[tests]]\nappel = "table(2)"\n', "attendu"),
        ('[[tests]]\nsortie = "2"\n', "organisation.main"),
        ('[[tests]]\nattendu = "2"\n', "a besoin de « appel »"),
        ("", "aucun test"),
    ],
)
def test_bad_tests_are_refused(workshop, visible, message):
    with pytest.raises(BankError, match=message):
        workshop.exercise(visible=visible)


def test_unknown_exercise(workshop):
    workshop.exercise()
    for name in ("absent", "../demo", "Demo", ""):
        with pytest.raises(BankError, match="exercice inconnu"):
            load_exercise(workshop.paths, name)


def test_order_must_list_every_exercise(workshop):
    workshop.exercise()
    assert [exercise.id for exercise in load_bank(workshop.paths)] == ["demo"]
    shutil.copytree(workshop.paths.exercises / "demo", workshop.paths.exercises / "oubli")
    with pytest.raises(BankError, match="oubli"):
        load_bank(workshop.paths)


def test_attempts_are_recorded(workshop, check):
    progress = Progress(workshop.paths.database)
    progress.record_attempt(check(SOLUTION), datetime(2026, 11, 23, 8, 30), 600)
    progress.record_attempt(check("x = y\n"), datetime(2026, 11, 23, 8, 40), None)
    first, second = progress.history("demo").attempts
    assert first.passed and first.seconds == 600 and first.hidden_ok == first.hidden_total == 2
    assert second.status is Status.NOT_ADMISSIBLE and second.seconds is None
    assert progress.history("autre").attempts == ()


def test_windows_line_endings_and_bom(check, workshop):
    exercise = workshop.exercise()
    workshop.student.mkdir(parents=True)
    data = b"\xef\xbb\xbf" + SOLUTION.replace("\n", "\r\n").encode()
    (workshop.student / "tables.py").write_bytes(data)
    verdict = verify(exercise, workshop.student)
    assert verdict.passed and verdict.remarks == []


def test_an_empty_folder_is_not_an_attempt(workshop, capsys):
    workshop.exercise()
    assert cli.main(["verifier", "demo"], workshop.paths) == 1
    assert "est vide" in capsys.readouterr().out
    assert workshop.student.is_dir()
    assert Progress(workshop.paths.database).history("demo").attempts == ()


def test_command_line(workshop, capsys):
    workshop.exercise()
    workshop.submit("def table(nombre, taille=3):\n    return []\n")
    assert cli.main(["verifier", "demo"], workshop.paths) == 1
    assert "TESTS RATÉS" in capsys.readouterr().out
    workshop.submit(SOLUTION)
    assert cli.main(["verifier"], workshop.paths) == 0
    output = capsys.readouterr().out
    assert "RÉUSSI" in output and "tentative n° 2" in output
    assert cli.main(["verifier", "absent"], workshop.paths) == 2
    assert "exercice inconnu" in capsys.readouterr().out


def test_pycharm_files(workshop):
    root = workshop.paths.root
    assert pycharm.configure(root, "demo")
    assert not pycharm.configure(root, "demo")
    module = root / ".idea" / f"{root.name}.iml"
    text = module.read_text(encoding="utf-8")
    assert 'excludeFolder url="file://$MODULE_DIR$/_prive"' in text
    assert 'sourceFolder url="file://$MODULE_DIR$/mes_solutions/demo"' in text
    assert f"{root.name}.iml" in (root / ".idea" / "modules.xml").read_text(encoding="utf-8")
    assert pycharm.configure(root, "autre")
    text = module.read_text(encoding="utf-8")
    assert "mes_solutions/autre" in text and "mes_solutions/demo" not in text


def test_pycharm_keeps_existing_settings(workshop):
    root = workshop.paths.root
    (root / ".idea").mkdir()
    module = root / ".idea" / "ancien.iml"
    module.write_text(
        '<module type="PYTHON_MODULE" version="4"><component name="NewModuleRootManager">'
        '<content url="file://$MODULE_DIR$"><excludeFolder url="file://$MODULE_DIR$/a" /></content>'
        '<orderEntry type="jdk" jdkName="Python 3.14" jdkType="Python SDK" />'
        "</component></module>",
        encoding="utf-8",
    )
    pycharm.configure(root, "demo")
    text = module.read_text(encoding="utf-8")
    assert "Python 3.14" in text and "MODULE_DIR$/a" in text and "_prive" in text
    assert not (root / ".idea" / f"{root.name}.iml").exists()
