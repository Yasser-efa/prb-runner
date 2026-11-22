"""Comparison of an expected result with an obtained one."""

import math

REL_TOLERANCE = 1e-9
ABS_TOLERANCE = 1e-9
_NUMBERS = (int, float)
_MISSING = object()


def same_value(expected: object, obtained: object) -> bool:
    """Compare with ``==``, except that floats are compared with a tolerance.

    Containers are compared element by element so that nested floats are tolerated
    too. A tuple never equals a list.

    :param expected: the reference value
    :param obtained: the value returned by the student's code
    :return: True if both values match
    """
    if isinstance(expected, float) or isinstance(obtained, float):
        return _same_number(expected, obtained)
    if isinstance(expected, (list, tuple)):
        return (
            type(expected) is type(obtained)
            and len(expected) == len(obtained)
            and all(map(same_value, expected, obtained, strict=True))
        )
    if isinstance(expected, dict):
        return _same_dict(expected, obtained)
    if isinstance(expected, (set, frozenset)):
        return _same_set(expected, obtained)
    return bool(expected == obtained)


def same_output(expected: str, obtained: str) -> bool:
    """Compare two texts, ignoring trailing spaces and trailing empty lines.

    :param expected: the reference text
    :param obtained: the text displayed by the student's code
    :return: True if both texts match
    """
    return normalize_output(expected) == normalize_output(obtained)


def normalize_output(text: str) -> str:
    """Remove trailing spaces on every line and trailing empty lines.

    :param text: any displayed text
    :return: the cleaned text
    """
    return "\n".join(line.rstrip() for line in text.split("\n")).rstrip("\n")


def type_difference(expected: object, obtained: object) -> str | None:
    """Find a value that is equal but not of the announced type (8.0 instead of 8).

    An int where a float is expected is fine, as it is for Python annotations.

    :param expected: the reference value
    :param obtained: a value already known to match
    :return: a description of the first difference, or None
    """
    if isinstance(expected, (list, tuple)) and isinstance(obtained, (list, tuple)):
        pairs = list(zip(expected, obtained, strict=False))
    elif isinstance(expected, dict) and isinstance(obtained, dict):
        pairs = [(expected[key], obtained[key]) for key in expected if key in obtained]
    else:
        pairs = []
    for left, right in pairs:
        found = type_difference(left, right)
        if found:
            return found
    suspicious = {(int, float), (int, bool), (bool, int), (bool, float)}
    if (type(expected), type(obtained)) in suspicious:
        return (
            f"renvoie {obtained!r} ({type(obtained).__name__}) "
            f"au lieu de {expected!r} ({type(expected).__name__})"
        )
    return None


def _same_number(expected: object, obtained: object) -> bool:
    if not (isinstance(expected, _NUMBERS) and isinstance(obtained, _NUMBERS)):
        return bool(expected == obtained)
    try:
        if math.isnan(expected) or math.isnan(obtained):
            return math.isnan(expected) and math.isnan(obtained)
        return math.isclose(expected, obtained, rel_tol=REL_TOLERANCE, abs_tol=ABS_TOLERANCE)
    except OverflowError:
        return bool(expected == obtained)


def _same_dict(expected: dict, obtained: object) -> bool:
    if not isinstance(obtained, dict) or len(expected) != len(obtained):
        return False
    remaining = dict(obtained)
    for key, value in expected.items():
        match = key if key in remaining else _find_match(key, remaining)
        if match is _MISSING or not same_value(value, remaining.pop(match)):
            return False
    return True


def _same_set(expected: set | frozenset, obtained: object) -> bool:
    if not isinstance(obtained, (set, frozenset)) or len(expected) != len(obtained):
        return False
    remaining = set(obtained)
    for item in expected:
        match = item if item in remaining else _find_match(item, remaining)
        if match is _MISSING:
            return False
        remaining.discard(match)
    return True


def _find_match(item: object, candidates) -> object:
    for candidate in candidates:
        if same_value(item, candidate):
            return candidate
    return _MISSING
