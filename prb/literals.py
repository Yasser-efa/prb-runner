"""Safe reading of Python values and calls written as text.

``ast.literal_eval`` cannot read back ``inf``, ``nan`` or ``frozenset``, which are
legitimate results, hence this slightly larger evaluator.
"""

import ast
from dataclasses import dataclass, field


class LiteralError(ValueError):
    """The text is not a plain Python value or call."""


@dataclass(frozen=True)
class Call:
    """A function call whose arguments are plain values."""

    source: str
    module: str | None
    function: str
    args: tuple = ()
    kwargs: dict = field(default_factory=dict)


def parse_literal(text: str) -> object:
    """Evaluate a plain Python value.

    :param text: the source of the value, for example ``"(1, [2.5, None])"``
    :return: the value
    :raises LiteralError: if the text is anything else than a plain value
    """
    return _evaluate(_parse_expression(text), text)


def parse_call(text: str) -> Call:
    """Read a call such as ``"table(3, taille=4)"`` or ``"tables.calculs.table(3)"``.

    :param text: the source of the call
    :return: the function name, its optional module and its evaluated arguments
    :raises LiteralError: if the text is not a call with plain arguments
    """
    node = _parse_expression(text)
    if not isinstance(node, ast.Call):
        raise LiteralError(f"« {text.strip()} » n'est pas un appel de fonction")
    module, function = _split_dotted_name(node.func, text)
    kwargs = {}
    for keyword in node.keywords:
        if keyword.arg is None:
            raise LiteralError(f"« ** » n'est pas accepté dans « {text.strip()} »")
        kwargs[keyword.arg] = _evaluate(keyword.value, text)
    return Call(
        source=text.strip(),
        module=module,
        function=function,
        args=tuple(_evaluate(arg, text) for arg in node.args),
        kwargs=kwargs,
    )


def _parse_expression(text: str) -> ast.expr:
    try:
        return ast.parse(text.strip(), mode="eval").body
    except (SyntaxError, ValueError) as error:
        raise LiteralError(f"« {text.strip()} » n'est pas une expression Python") from error


def _split_dotted_name(node: ast.expr, text: str) -> tuple[str | None, str]:
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        raise LiteralError(f"nom de fonction illisible dans « {text.strip()} »")
    parts.append(node.id)
    parts.reverse()
    return ".".join(parts[:-1]) or None, parts[-1]


def _evaluate(node: ast.expr, text: str) -> object:
    match node:
        case ast.Constant() if node.value is not Ellipsis:
            return node.value
        case ast.Tuple():
            return tuple(_evaluate(item, text) for item in node.elts)
        case ast.List():
            return [_evaluate(item, text) for item in node.elts]
        case ast.Set():
            return {_evaluate(item, text) for item in node.elts}
        case ast.Dict() if None not in node.keys:
            return {
                _evaluate(key, text): _evaluate(value, text)
                for key, value in zip(node.keys, node.values, strict=True)
            }
        case ast.Name(id="inf" | "nan"):
            return float(node.id)
        case ast.UnaryOp(op=ast.USub() | ast.UAdd()):
            value = _evaluate(node.operand, text)
            if isinstance(value, (int, float, complex)):
                return -value if isinstance(node.op, ast.USub) else +value
        case ast.BinOp(op=ast.Add() | ast.Sub()):
            left, right = _evaluate(node.left, text), _evaluate(node.right, text)
            if isinstance(left, (int, float)) and isinstance(right, complex):
                return left + right if isinstance(node.op, ast.Add) else left - right
        case ast.Call(func=ast.Name(id="set" | "frozenset"), keywords=[]) if len(node.args) <= 1:
            builder = set if node.func.id == "set" else frozenset
            return builder(_evaluate(node.args[0], text)) if node.args else builder()
    raise LiteralError(f"« {text.strip()} » contient autre chose que des valeurs simples")
