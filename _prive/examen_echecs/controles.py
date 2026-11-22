"""Controls of the chess exam: the board is displayed with terminal colours."""

import re

_CELL = re.compile(
    "\x1b\\[(?P<ink>30|38;5;231)m\x1b\\[(?P<background>48;5;33|103)m"
    "\u2005(?P<symbol>.)\u2005\x1b\\[0m"
)
_LETTERS = {"♜": "T", "♝": "F", "♛": "D", "♚": "R", "\u3000": " "}
_BLACK_INK, _BLACK_BACKGROUND = "30", "48;5;33"


def _simplify(match):
    letter = _LETTERS[match["symbol"]]
    if match["ink"] == _BLACK_INK:
        letter = letter.lower()
    return letter + (":" if match["background"] == _BLACK_BACKGROUND else ".")


def echiquier_simplifie(outcome, case):
    """Replace every coloured cell by two letters, and ignore empty lines."""
    text = _CELL.sub(_simplify, outcome.output)
    text = text.replace("’", "'").replace("–", "-")
    return "\n".join(line.rstrip() for line in text.split("\n") if line.strip())
