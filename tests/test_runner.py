import time

import pytest

from prb.runner import run_cases

PROGRAM = '''titre = "Programme"
reference = "test"
sorte = "programme"

[organisation]
fichiers = ["main.py"]
main = "main.py"
'''
PROGRAM_TEST = '''[[tests]]
entree = ["4"]
sortie = "Nombre ? 4\\n8"
'''


@pytest.fixture
def run(workshop):
    """Run the two visible cases of the demo exercise on some code."""

    def execute(code, timeout=2.0, description=None, visible=None):
        options = {}
        if description:
            options["description"] = description
        if visible:
            options["visible"] = visible
        exercise = workshop.exercise(hidden="", **options)
        folder = workshop.submit(code)
        return run_cases(folder, exercise.visible_cases, exercise.main, timeout)

    return execute


@pytest.fixture
def run_program(run):
    def execute(code):
        files = code if isinstance(code, dict) else {"main.py": code}
        return run(files, description=PROGRAM, visible=PROGRAM_TEST).outcomes[0]

    return execute


def test_values_are_returned(run):
    report = run("def table(nombre, taille=3):\n    return [nombre] * taille\n")
    assert [outcome.status for outcome in report.outcomes] == ["value", "value"]
    assert [outcome.value for outcome in report.outcomes] == [[2, 2, 2], [5, 5]]
    assert report.noisy_modules == []


def test_tuples_stay_tuples(run):
    outcome = run("def table(nombre, taille=3):\n    return (nombre, taille)\n").outcomes[0]
    assert outcome.plain and outcome.value == (2, 3) and type(outcome.value) is tuple


@pytest.mark.parametrize(
    ("expression", "value"),
    [
        ("float('inf')", float("inf")),
        ("frozenset({1})", frozenset({1})),
        ("__import__('collections').Counter('aab')", {"a": 2, "b": 1}),
        ("{(1, 2): None}", {(1, 2): None}),
        ("'é\\n\\u2713'", "é\n✓"),
    ],
)
def test_unusual_values(run, expression, value):
    outcome = run(f"def table(nombre, taille=3):\n    return {expression}\n").outcomes[0]
    assert outcome.plain and outcome.value == value


@pytest.mark.parametrize("expression", ["range(3)", "map(str, [1])", "table", "10 ** 5000"])
def test_values_that_cannot_be_compared(run, expression):
    outcome = run(f"def table(nombre, taille=3):\n    return {expression}\n").outcomes[0]
    assert outcome.status == "value" and not outcome.plain


def test_exception_points_to_the_student_line(run):
    code = "def aide(liste):\n    return liste[9]\n\n\n"
    code += "def table(nombre, taille=3):\n    return aide([])\n"
    outcome = run(code).outcomes[0]
    assert outcome.status == "exception"
    error = outcome.error
    assert (error.type, error.message) == ("IndexError", "list index out of range")
    assert (error.file, error.line, error.function) == ("tables.py", 2, "aide")
    assert error.source == "return liste[9]"


def test_exception_inside_the_library_points_to_the_caller(run):
    code = "import json\n\n\ndef table(nombre, taille=3):\n    return json.loads('{')\n"
    error = run(code).outcomes[0].error
    assert error.type == "JSONDecodeError"
    assert (error.file, error.line) == ("tables.py", 5)


def test_infinite_loop_is_stopped_and_located(run):
    code = "def table(nombre, taille=3):\n    while nombre:\n        taille += 1\n    return []\n"
    start = time.perf_counter()
    report = run(code, timeout=0.5)
    assert time.perf_counter() - start < 6
    assert [outcome.status for outcome in report.outcomes] == ["timeout", "timeout"]
    error = report.outcomes[0].error
    assert error.file == "tables.py" and error.line in (2, 3) and error.function == "table"


def test_cases_after_a_timeout_still_run(run):
    code = (
        "def table(nombre, taille=3):\n    while nombre == 2:\n        taille += 1\n"
        "    return [5, 10]\n"
    )
    report = run(code, timeout=0.5)
    assert [outcome.status for outcome in report.outcomes] == ["timeout", "value"]


def test_infinite_loop_during_import(run):
    code = "while True:\n    pass\n\n\ndef table(nombre, taille=3):\n    return []\n"
    report = run(code, timeout=0.5)
    assert {outcome.status for outcome in report.outcomes} == {"timeout"}
    assert report.outcomes[0].error.file == "tables.py"


def test_a_bare_except_cannot_hide_a_timeout(run):
    code = (
        "def table(nombre, taille=3):\n    while True:\n        try:\n            taille += 1\n"
        "        except:\n            pass\n"
    )
    assert run(code, timeout=0.5).outcomes[0].status == "timeout"


def test_too_many_timeouts_skip_the_rest(run):
    visible = "".join(
        f'[[tests]]\nappel = "table({number})"\nattendu = "[]"\n' for number in range(4)
    )
    code = "def table(nombre, taille=3):\n    while True:\n        pass\n"
    report = run(code, 0.3, visible=visible)
    assert [o.status for o in report.outcomes] == ["timeout", "timeout", "skipped", "skipped"]


def test_a_slow_function_does_not_stop_the_others(workshop):
    description = (
        'titre = "T"\nreference = "t"\nsorte = "fonction"\n[organisation]\nfichiers = ["m.py"]\n'
        '[[fonctions]]\nmodule = "m"\nsignature = "lente(n: int) -> int"\n'
        '[[fonctions]]\nmodule = "m"\nsignature = "rapide(n: int) -> int"\n'
    )
    calls = ["lente(1)", "lente(2)", "lente(3)", "rapide(4)"]
    visible = "".join(f'[[tests]]\nappel = "{call}"\nattendu = "4"\n' for call in calls)
    exercise = workshop.exercise(description, visible, "", {"m.py": ""})
    code = "def lente(n):\n    while n:\n        pass\n\n\ndef rapide(n):\n    return n\n"
    report = run_cases(workshop.submit({"m.py": code}), exercise.visible_cases, timeout=0.3)
    statuses = [outcome.status for outcome in report.outcomes]
    assert statuses == ["timeout", "timeout", "skipped", "value"]


def test_endless_display_is_stopped(run):
    code = "def table(nombre, taille=3):\n    while True:\n        print('a' * 1000)\n"
    outcome = run(code).outcomes[0]
    assert outcome.status == "flood" and outcome.error.line == 3


def test_recursion(run):
    outcome = run("def table(nombre, taille=3):\n    return table(nombre)\n").outcomes[0]
    assert outcome.status == "exception" and outcome.error.type == "RecursionError"


def test_exit_is_reported_for_a_function(run):
    outcome = run("def table(nombre, taille=3):\n    exit()\n").outcomes[0]
    assert outcome.status == "exception" and outcome.error.type == "SystemExit"


def test_brutal_stop(run):
    report = run("import os\n\n\ndef table(nombre, taille=3):\n    os._exit(3)\n")
    assert [outcome.status for outcome in report.outcomes] == ["crash", "crash"]


def test_import_error(run):
    report = run("import tables_absent\n\n\ndef table(nombre, taille=3):\n    return []\n")
    assert {outcome.status for outcome in report.outcomes} == {"exception"}
    assert all(outcome.during_import for outcome in report.outcomes)
    assert report.outcomes[0].error.line == 1


def test_module_that_displays_when_imported(run):
    report = run("print('coucou')\n\n\ndef table(nombre, taille=3):\n    return []\n")
    assert report.noisy_modules == ["tables"]


def test_input_at_import_does_not_block(run):
    report = run("x = input()\n\n\ndef table(nombre, taille=3):\n    return []\n")
    assert report.outcomes[0].error.type == "EOFError"


def test_modified_arguments_are_detected(workshop):
    description = (
        'titre = "T"\nreference = "t"\nsorte = "fonction"\n[organisation]\nfichiers = ["m.py"]\n'
        '[[fonctions]]\nmodule = "m"\nsignature = "f(liste: list, autre: int = 1) -> int"\n'
        "preserve_arguments = true\n"
    )
    visible = '[[tests]]\nappel = "f([1, 2])"\nattendu = "2"\n'
    visible += '[[tests]]\nappel = "f(liste=[1, 2], autre=2)"\nattendu = "2"\n'
    exercise = workshop.exercise(description, visible, "", {"m.py": ""})
    folder = workshop.submit({"m.py": "def f(liste, autre=1):\n    return liste.pop()\n"})
    outcomes = run_cases(folder, exercise.visible_cases).outcomes
    assert [outcome.modified for outcome in outcomes] == [(0,), ("liste",)]
    folder = workshop.submit({"m.py": "def f(liste, autre=1):\n    return sorted(liste).pop()\n"})
    outcomes = run_cases(folder, exercise.visible_cases).outcomes
    assert [outcome.modified for outcome in outcomes] == [(), ()]


def test_a_module_level_list_is_shared_between_calls(run):
    code = "vu = []\n\n\ndef table(nombre, taille=3):\n    vu.append(nombre)\n    return vu\n"
    assert [outcome.value for outcome in run(code).outcomes] == [[2], [2, 5]]


def test_program_shows_prompts_and_typed_text(run_program):
    outcome = run_program("nombre = int(input('Nombre ? '))\nprint(nombre * 2)\n")
    assert outcome.status == "value"
    assert outcome.output == "Nombre ? 4\n8\n"


def test_program_imports_its_own_modules(run_program):
    files = {
        "main.py": (
            "from calculs.doubles import double\n\n\ndef main():\n"
            "    print(double(int(input('Nombre ? '))))\n\n\n"
            "if __name__ == '__main__':\n    main()\n"
        ),
        "calculs/__init__.py": "",
        "calculs/doubles.py": "def double(nombre):\n    return nombre * 2\n",
    }
    assert run_program(files).output == "Nombre ? 4\n8\n"


def test_program_that_reads_too_much(run_program):
    outcome = run_program("input()\ninput()\n")
    assert outcome.status == "exception"
    error = outcome.error
    assert (error.type, error.file, error.line) == ("EOFError", "main.py", 2)


def test_program_can_read_stdin_directly(run_program):
    assert run_program("import sys\nprint(sys.stdin.read())\n").output == "4\n\n"


def test_program_may_exit_normally(run_program):
    assert run_program("import sys\nprint('a')\nsys.exit()\n").status == "value"
    assert run_program("import sys\nsys.exit(1)\n").error.type == "SystemExit"


def test_the_original_folder_is_untouched(workshop, run):
    run("open('trace.txt', 'w').close()\n\n\ndef table(nombre, taille=3):\n    return []\n")
    assert sorted(path.name for path in workshop.student.iterdir()) == ["tables.py"]
