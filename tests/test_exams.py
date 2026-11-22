"""What long exercises need: provided files, controls, seeds, values after the call."""

import io
import zipfile
from datetime import datetime

import pytest
from rich.console import Console

from prb import cli
from prb.model import BankError
from prb.progress import Progress
from prb.report import show_verdict
from prb.scheduler import read_state
from prb.screens import layout_tree
from prb.validation import validate_exercise
from prb.verdict import Status, verify
from prb.workspace import archive_folder, prepare_folder
from tests.conftest import SOLUTION

PROVIDED = '''titre = "Fournis"
reference = "test"
sorte = "fonction"
duree_minutes = 120

[organisation]
fichiers = ["jeu/__init__.py", "jeu/regles.py"]
modifiables = ["jeu/exemples.py"]

[organisation.fournis]
"jeu/outils.py" = "cours/outils.py"
"jeu/exemples.py" = "cours/archive.zip::exemples.py"
"donnees/liste.txt" = "cours/liste.txt"

[[fonctions]]
module = "jeu.regles"
signature = "lire(chemin: str = ...) -> list[str]"
'''
OUTILS = "def Mauvais_Style(l):\n    return int(l)\n"
REGLES = '''"""Lecture de fichiers."""

from jeu.exemples import PREFIXE
from jeu.outils import Mauvais_Style


def lire(chemin: str = "donnees/liste.txt") -> list[str]:
    """
    Lit les lignes d'un fichier.

    :param chemin: le fichier à lire
    :return: les lignes
    """
    with open(chemin, encoding="utf-8") as fichier:
        return [f"{PREFIXE}{Mauvais_Style(ligne)}" for ligne in fichier]
'''
VISIBLE = '[[tests]]\nappel = "lire()"\nattendu = "[\'n1\', \'n2\']"\n'
HIDDEN = '[[groupes]]\ntheme = "fichiers"\nappels = ["lire(\'donnees/secret.txt\')"]\n'
GOOD = {"jeu/__init__.py": "", "jeu/regles.py": REGLES}


@pytest.fixture
def exam(workshop):
    """An exercise with provided files, one of them inside a ZIP archive."""
    root = workshop.paths.root
    workshop.write(root / "cours", {"outils.py": OUTILS, "liste.txt": "1\n2\n"})
    with zipfile.ZipFile(root / "cours" / "archive.zip", "w") as archive:
        archive.writestr("exemples.py", 'PREFIXE = "n"\n')
    workshop.write(workshop.paths.private / "demo/fichiers", {"donnees/secret.txt": "7\n"})
    return workshop.exercise(PROVIDED, VISIBLE, HIDDEN, GOOD)


@pytest.fixture
def submit(workshop, exam):
    def run(files):
        prepare_folder(workshop.paths, exam, restore=True)
        workshop.submit(files)
        return verify(exam, workshop.student)

    return run


def test_provided_files_are_copied_and_usable(workshop, submit):
    verdict = submit(GOOD)
    assert verdict.status is Status.PASSED
    assert (workshop.student / "jeu/exemples.py").read_text() == 'PREFIXE = "n"\n'
    assert not (workshop.student / "donnees/secret.txt").exists()


def test_provided_files_are_not_judged(submit):
    assert submit(GOOD).remarks == []


def test_modified_provided_file_is_refused(submit):
    verdict = submit(GOOD | {"jeu/outils.py": OUTILS + "# petite note\n"})
    assert [problem.file for problem in verdict.admissibility] == ["jeu/outils.py"]
    assert "modifié" in verdict.admissibility[0].message


def test_line_endings_of_a_provided_file_do_not_matter(submit, workshop):
    submit(GOOD)
    (workshop.student / "jeu/outils.py").write_bytes(OUTILS.replace("\n", "\r\n").encode())
    assert submit(GOOD).status is Status.PASSED


def test_editable_provided_file_may_change(submit):
    verdict = submit(GOOD | {"jeu/exemples.py": 'PREFIXE = "n"\nAUTRE = 3\n'})
    assert verdict.status is Status.PASSED


def test_missing_provided_file(workshop, exam):
    workshop.submit(GOOD)
    messages = [problem.message for problem in verify(exam, workshop.student).admissibility]
    assert any("fichier fourni manquant" in message for message in messages)
    prepare_folder(workshop.paths, exam)
    assert not (workshop.student / "jeu/outils.py").exists()
    prepare_folder(workshop.paths, exam, restore=True)
    assert verify(exam, workshop.student).passed


def test_original_that_cannot_be_found(workshop, exam):
    (workshop.paths.root / "cours/outils.py").unlink()
    with pytest.raises(BankError, match="fichier fourni introuvable"):
        prepare_folder(workshop.paths, exam)


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        ('"cours/outils.py"', '"../outils.py"', "chemin invalide"),
        ('"jeu/outils.py" =', '"jeu/regles.py" =', "demandé et fourni"),
        ('modifiables = ["jeu/exemples.py"]', 'modifiables = ["jeu/x.py"]', "non fourni"),
        ('"jeu/outils.py" =', '"random.py" =', "masque un module"),
    ],
)
def test_bad_layouts(workshop, exam, old, new, message):
    with pytest.raises(BankError, match=message):
        workshop.exercise(PROVIDED.replace(old, new), VISIBLE, HIDDEN, GOOD)


def test_any_default_value_is_accepted(submit):
    other = REGLES.replace('= "donnees/liste.txt"', "= CHEMIN").replace(
        "\n\n\ndef", '\n\nCHEMIN = "donnees/" + "liste.txt"\n\n\ndef'
    )
    assert submit(GOOD | {"jeu/regles.py": other}).status is Status.PASSED
    without = REGLES.replace(' = "donnees/liste.txt"', "")
    verdict = submit(GOOD | {"jeu/regles.py": without})
    assert "chemin=..." in verdict.admissibility[0].message


def test_open_without_encoding_is_a_remark(submit):
    verdict = submit(GOOD | {"jeu/regles.py": REGLES.replace(', encoding="utf-8"', "")})
    assert verdict.passed and "open() sans encodage" in verdict.remarks[0].message


def test_tree_shows_provided_files(exam):
    console = Console(width=80, record=True, file=io.StringIO())
    console.print(layout_tree(exam))
    text = console.export_text()
    assert "outils.py  (fourni, à ne pas modifier)" in text
    assert "exemples.py  (fourni, modifiable)" in text


def test_review_archives_and_restores(workshop, exam):
    now = datetime(2026, 11, 23, 8, 0)
    prepare_folder(workshop.paths, exam)
    assert archive_folder(workshop.paths, exam, now) is None
    workshop.submit(GOOD)
    archive = archive_folder(workshop.paths, exam, now)
    assert (archive / "jeu/regles.py").exists()
    prepare_folder(workshop.paths, exam)
    names = {path.name for path in workshop.student.rglob("*") if path.is_file()}
    assert names == {"outils.py", "exemples.py", "liste.txt"}


def test_provided_files_alone_are_not_an_attempt(workshop, exam, capsys):
    assert cli.main(["verifier", "demo"], workshop.paths) == 1
    assert "mes_solutions/demo/ est vide" in capsys.readouterr().out
    assert Progress(workshop.paths.database).history("demo").attempts == ()


def test_long_exercises_have_long_sessions(workshop, exam, capsys):
    now = datetime(2026, 11, 28, 9, 0)
    cli.main(["du_jour"], workshop.paths, now)
    assert "les fichiers fournis sont déjà dans le dossier" in capsys.readouterr().out
    workshop.submit(GOOD | {"jeu/regles.py": "x = 1\n"})
    cli.main(["verifier"], workshop.paths, now.replace(hour=11, minute=20))
    history = Progress(workshop.paths.database).history("demo")
    assert history.sessions[0].limit_minutes == 150
    assert read_state(history).seconds == 140 * 60


def test_exam_is_validated_with_its_provided_files(workshop, exam):
    statement = "jeu donnees regles.py outils.py exemples.py lire\n>>> lire()\n['n1', 'n2']\n"
    workshop.write(workshop.paths.exercises / "demo", {"enonce.md": statement})
    problems = validate_exercise(workshop.paths, "demo").problems
    assert problems == ["moins de 6 tests cachés", "il faut 2 ou 3 indices"]


# Values after the call, controls and seeds

GAME = '''titre = "Jeu"
reference = "test"
sorte = "programme"

[organisation]
fichiers = ["main.py", "jeu.py"]
main = "main.py"

[[fonctions]]
module = "jeu"
signature = "doubler(nombres: list[int], fois: int = 1) -> None"

[[fonctions]]
module = "jeu"
signature = "comparer(a: int, b: int) -> int"

[[fonctions]]
module = "jeu"
signature = "chercher(texte: str) -> bool"

[[fonctions]]
module = "jeu"
signature = "demander(invite: str) -> int"
'''
JEU = '''import re


def doubler(nombres, fois=1):
    for _ in range(fois):
        for rang, nombre in enumerate(nombres):
            nombres[rang] = nombre * 2


def comparer(a, b):
    return a - b


def chercher(texte):
    return re.search("a+", texte)


def demander(invite):
    reponse = input(invite)
    while not reponse.isdigit():
        print("Encore !")
        reponse = input(invite)
    return int(reponse)
'''
MAIN = '''import random


def main():
    print("Début")
    print()
    print(random.randint(1, 10 ** 9), input("? "))


if __name__ == "__main__":
    main()
'''
GAME_VISIBLE = '''[[tests]]
appel = "doubler([1, 2])"
apres = "nombres"
attendu = "[2, 4]"

[[tests]]
appel = "doubler(nombres=[1], fois=3)"
apres = "nombres"
attendu = "[8]"

[[tests]]
appel = "comparer(3, 9)"
controle = "signe"
attendu = "-1"

[[tests]]
appel = "chercher('baab')"
controle = "booleen"
attendu = "True"

[[tests]]
appel = "chercher('xyz')"
controle = "booleen"
attendu = "False"

[[tests]]
libelle = "demander(...)"
appel = "demander('? ')"
entree = ["x", "12"]
attendu = "12"

[[tests]]
controle = "premiere_ligne"
attendu = "'Début'"
entree = ["a"]

[[tests]]
graine = 1
controle = "sans_lignes_vides"
entree = ["a"]
sortie = """
Début
? a
144272510 a
"""
'''
GAME_HIDDEN = '''[[groupes]]
theme = "graine"
graine = 5
controle = "sans_lignes_vides"
entrees = [["b"]]

[[groupes]]
theme = "autre graine"
graine = 6
controle = "sans_lignes_vides"
entrees = [["b"]]

[[groupes]]
theme = "saisies"
ignorer_sortie = true
tests = [{ appel = "demander('')", entree = ["", "7"] }]

[[groupes]]
theme = "modification"
apres = "nombres"
appels = ["doubler([])", "doubler([5, 0], 2)"]
'''
CONTROLS = "def premiere_ligne(outcome, case):\n    return outcome.output.splitlines()[0]\n"


@pytest.fixture
def play(workshop):
    def run(files=None, visible=GAME_VISIBLE, hidden=GAME_HIDDEN):
        workshop.write(workshop.paths.private / "demo", {"controles.py": CONTROLS})
        good = {"main.py": MAIN, "jeu.py": JEU}
        exercise = workshop.exercise(GAME, visible, hidden, good)
        return verify(exercise, workshop.submit(good | (files or {})))

    return run


def display(verdict):
    console = Console(file=io.StringIO(), width=160)
    show_verdict(console, verdict)
    return console.file.getvalue()


def test_everything_passes(play):
    verdict = play()
    assert verdict.status is Status.PASSED, display(verdict)
    text = display(verdict)
    assert "valeur de nombres après l'appel" in text and "demander(...)" in text


def test_value_after_the_call(play):
    code = JEU.replace("nombres[rang] = nombre * 2", "pass")
    verdict = play({"jeu.py": code})
    assert [report.ok for report in verdict.visible[:2]] == [False, False]
    assert "[1, 2]" in display(verdict)


def test_any_value_of_the_right_sign_is_accepted(play):
    assert play({"jeu.py": JEU.replace("return a - b", "return (a - b) * 100")}).passed
    verdict = play({"jeu.py": JEU.replace("return a - b", "return b - a")})
    assert not verdict.visible[2].ok and "1" in display(verdict)


def test_any_true_value_is_accepted(play):
    assert play({"jeu.py": JEU.replace("return re.search(", "return bool(re.search(")
                 .replace('"a+", texte)', '"a+", texte))')}).passed
    assert not play({"jeu.py": JEU.replace("return re.search", "return not re.search")}).passed


def test_seeds_make_programs_comparable(play):
    assert play().passed
    other = MAIN.replace("random.randint(1, 10 ** 9)", "random.randint(2, 10 ** 9)")
    verdict = play({"main.py": other})
    assert [report.ok for report in verdict.hidden[:2]] == [False, False]


def test_messages_of_an_interactive_function_are_free(play):
    verdict = play({"jeu.py": JEU.replace("Encore !", "Un nombre, svp.")})
    assert verdict.passed and not any("affiche du texte" in r.message for r in verdict.remarks)


def test_empty_lines_can_be_ignored(play):
    assert play({"main.py": MAIN.replace("    print()\n", "")}).passed


def test_unreadable_result_is_a_failure(play):
    verdict = play({"jeu.py": JEU.replace("return a - b", "return 'abc'")})
    assert verdict.status is Status.FAILED
    assert "résultat illisible (TypeError)" in display(verdict)


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        ('controle = "signe"', 'controle = "absent"', "contrôle inconnu"),
        ('apres = "nombres"', 'apres = "absent"', "« apres » doit être un paramètre"),
        ("libelle", "label", "clé inconnue"),
        ('controle = "premiere_ligne"\n', "", "« attendu » a besoin"),
    ],
)
def test_bad_options(play, old, new, message):
    with pytest.raises(BankError, match=message):
        play(visible=GAME_VISIBLE.replace(old, new, 1))


def test_broken_controls_file(workshop, play):
    play()
    workshop.write(workshop.paths.private / "demo", {"controles.py": "1 / 0\n"})
    with pytest.raises(BankError, match="controles.py"):
        workshop.exercise(GAME, GAME_VISIBLE, GAME_HIDDEN, {"jeu.py": SOLUTION})
