import math

import pytest

from prb.comparison import normalize_output, same_output, same_value, type_difference
from prb.literals import LiteralError, parse_call, parse_literal


@pytest.mark.parametrize(
    ("expected", "obtained"),
    [
        (0.3, 0.1 + 0.2),
        (0.0, 1e-17),
        ([1, (0.3, "a")], [1, (0.1 + 0.2, "a")]),
        ({"a": 0.3}, {"a": 0.1 + 0.2}),
        ({0.3: "a"}, {0.1 + 0.2: "a"}),
        ({0.3, 1}, {1, 0.1 + 0.2}),
        (math.inf, math.inf),
        (math.nan, math.nan),
        (2, 2.0),
        (set(), set()),
        ({None: 1}, {None: 1}),
        ({None}, {None}),
        (10**400, 10**400),
    ],
)
def test_equal_values(expected, obtained):
    assert same_value(expected, obtained)


@pytest.mark.parametrize(
    ("expected", "obtained"),
    [
        ((1, 2), [1, 2]),
        ([1, 2], (1, 2)),
        ([(1, 2)], [[1, 2]]),
        (0.3, 0.3001),
        ([0.3], [0.3, 0.3]),
        ("2", 2),
        (2, "2"),
        (None, 0),
        (0, None),
        ({1: "a"}, {1: "b"}),
        ({1: "a"}, {2: "a"}),
        ({None: 1}, {2: 1}),
        ({1, 2}, {1, 3}),
        ({None}, {1}),
        ({1, 2}, [1, 2]),
        (1.0, "1.0"),
        (1.0, None),
        (10**400, 1.0),
        ("a", "A"),
    ],
)
def test_different_values(expected, obtained):
    assert not same_value(expected, obtained)


def test_output_ignores_trailing_spaces_only():
    assert same_output("a  \nb\n\n", "a\nb")
    assert not same_output("a\nb", "a\n b")
    assert not same_output("a\nb", "a\n\nb")
    assert normalize_output("a \r\nb") == "a\nb"


@pytest.mark.parametrize(
    ("expected", "obtained", "found"),
    [(8, 8.0, True), ((8, 7), (8.0, 7), True), (True, 1, True), (2.0, 2, False), (8, 8, False)],
)
def test_type_difference(expected, obtained, found):
    assert bool(type_difference(expected, obtained)) is found


@pytest.mark.parametrize(
    "value",
    [
        (1, -2.5, "é\n'"),
        [None, True, {1: {2, 3}}],
        set(),
        frozenset({1}),
        b"x",
        2 + 3j,
        math.inf,
        -math.inf,
        ((),),
    ],
)
def test_literals_survive_a_round_trip(value):
    assert parse_literal(repr(value)) == value


@pytest.mark.parametrize("text", ["print(1)", "a", "[x]", "1 +", "f'{1}'", "...", "{**{}}"])
def test_anything_else_is_refused(text):
    with pytest.raises(LiteralError):
        parse_literal(text)


def test_calls_are_parsed():
    call = parse_call("paquet.module.f((1, 2), [None], cle={'a': 1})")
    assert (call.module, call.function) == ("paquet.module", "f")
    assert call.args == ((1, 2), [None])
    assert call.kwargs == {"cle": {"a": 1}}


@pytest.mark.parametrize("text", ["f", "f(x)", "f(**{})", "f(1)(2)", "3"])
def test_bad_calls_are_refused(text):
    with pytest.raises(LiteralError):
        parse_call(text)
