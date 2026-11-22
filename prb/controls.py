"""Controls: functions that extract what must be compared from what happened.

They make it possible to test a function whose result is partly free (random choices, layout of
the display). A control receives the outcome and the case, and returns a plain value. Exercises
can define their own in ``_prive/<id>/controles.py``.
"""

import importlib.util
from collections.abc import Callable
from pathlib import Path

from prb.comparison import normalize_output
from prb.model import BankError


def truth_value(outcome, case) -> bool:
    """Compare only the truth value of the result."""
    return outcome.truth


def sign(outcome, case) -> int:
    """Compare only the sign of the result."""
    return (outcome.value > 0) - (outcome.value < 0)


def without_empty_lines(outcome, case) -> str:
    """Compare the display, ignoring empty lines."""
    lines = normalize_output(outcome.output).split("\n")
    return "\n".join(line for line in lines if line)


BUILT_IN: dict[str, Callable] = {
    "booleen": truth_value,
    "signe": sign,
    "sans_lignes_vides": without_empty_lines,
}


def load_controls(path: Path) -> dict[str, Callable]:
    """Load the controls available to an exercise.

    :param path: the file defining its own controls, which may not exist
    :return: the controls, indexed by name
    """
    controls = dict(BUILT_IN)
    if not path.is_file():
        return controls
    spec = importlib.util.spec_from_file_location(f"controles_{path.parent.name}", path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as error:
        raise BankError(f"{path.parent.name}/{path.name} : {error}") from error
    for name, value in vars(module).items():
        if callable(value) and not name.startswith("_"):
            controls[name] = value
    return controls


def apply_control(case, outcome) -> object:
    """Run the control of a case, which may stumble on an unexpected result.

    :param case: a case with a control
    :param outcome: what happened
    :return: the value to compare
    """
    try:
        return case.control(outcome, case)
    except Exception as error:
        return f"résultat illisible ({type(error).__name__})"
