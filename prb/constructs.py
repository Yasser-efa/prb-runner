"""Python constructs that an exercise can forbid or require.

The names on the left are the ones written in ``exercice.toml``.
"""

import ast
from collections.abc import Callable


def _is_endless_while(node: ast.AST) -> bool:
    """Tell whether a node is ``while True``, ``while 1`` or an equivalent."""
    if not isinstance(node, ast.While):
        return False
    test, expected = node.test, True
    while isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
        test, expected = test.operand, not expected
    return isinstance(test, ast.Constant) and bool(test.value) is expected


def _is_slice(node: ast.AST) -> bool:
    return isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Slice)


def _is_dict(node: ast.AST) -> bool:
    return isinstance(node, (ast.Dict, ast.DictComp))


def _is_set(node: ast.AST) -> bool:
    return isinstance(node, (ast.Set, ast.SetComp))


def _is_list(node: ast.AST) -> bool:
    literal = isinstance(node, ast.List) and isinstance(node.ctx, ast.Load)
    return literal or isinstance(node, ast.ListComp)


def _instance_of(*types: type[ast.AST]) -> Callable[[ast.AST], bool]:
    return lambda node: isinstance(node, types)


CONSTRUCTS: dict[str, Callable[[ast.AST], bool]] = {
    "break": _instance_of(ast.Break),
    "continue": _instance_of(ast.Continue),
    "try": _instance_of(ast.Try, ast.TryStar),
    "while True": _is_endless_while,
    "while": _instance_of(ast.While),
    "for": _instance_of(ast.For),
    "if": _instance_of(ast.If),
    "match": _instance_of(ast.Match),
    "with": _instance_of(ast.With),
    "lambda": _instance_of(ast.Lambda),
    "global": _instance_of(ast.Global),
    "ternaire": _instance_of(ast.IfExp),
    "compréhension": _instance_of(ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp),
    "tranche": _is_slice,
    "f-string": _instance_of(ast.JoinedStr),
    "dictionnaire": _is_dict,
    "ensemble": _is_set,
    "liste": _is_list,
}
