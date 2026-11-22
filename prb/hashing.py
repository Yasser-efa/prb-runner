"""Detection of lists, dictionaries and sets used as set elements or dictionary keys.

PyCharm shows these mistakes as errors. Only certain cases are reported: a variable counts
only if every value it receives in its scope is of the same kind.
"""

import ast
from collections.abc import Iterator
from dataclasses import dataclass, field

from prb.sources import Problem, SourceFile

_FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)
_BUILDERS = {"list": "list", "sorted": "list", "dict": "dict", "set": "set"}
_LIST_METHODS = {"split", "rsplit", "splitlines", "readlines", "findall"}
_ANNOTATIONS = {"list", "dict", "set", "List", "Dict", "Set"}
_ELEMENT, _KEY = "un élément d'ensemble", "une clé de dictionnaire"
_METHODS = {
    "set": ({"add", "remove", "discard"}, _ELEMENT),
    "dict": ({"get", "setdefault", "pop"}, _KEY),
}
_FRENCH = {
    "list": "une liste",
    "dict": "un dictionnaire",
    "set": "un ensemble",
    "tuple": "un tuple qui contient une liste, un dictionnaire ou un ensemble",
}
_PASSES = 3


@dataclass
class _Scope:
    """What is known of the names that some code can use.

    A variable has a kind and the line from which this kind is certain.
    """

    variables: dict[str, tuple[str, int]] = field(default_factory=dict)
    returns: dict[str, str | None] = field(default_factory=dict)

    def kind(self, node: ast.expr) -> str | None:
        """Name the unhashable type of an expression, None if it is hashable or unknown."""
        match node:
            case ast.List() | ast.ListComp():
                return "list"
            case ast.Dict() | ast.DictComp():
                return "dict"
            case ast.Set() | ast.SetComp():
                return "set"
            case ast.Tuple(elts=items):
                return "tuple" if any(self.kind(item) for item in items) else None
            case ast.Name(id=name):
                kind, line = self.variables.get(name, (None, 0))
                return kind if node.lineno > line else None
            case ast.Subscript(value=value, slice=ast.Slice()):
                return "list" if self.kind(value) == "list" else None
            case ast.BinOp(left=left, op=ast.Add() | ast.Mult(), right=right):
                return "list" if "list" in (self.kind(left), self.kind(right)) else None
            case ast.Call(func=ast.Name(id=name)):
                return self.returns[name] if name in self.returns else _BUILDERS.get(name)
            case ast.Call(func=ast.Attribute(attr=name)) if name in _LIST_METHODS:
                return "list"
        return None

    def element_kind(self, node: ast.expr) -> str | None:
        """Name the unhashable type of everything in a list or tuple written in the code."""
        if not isinstance(node, (ast.List, ast.Tuple)):
            return None
        kinds = {self.kind(item) for item in node.elts}
        return kinds.pop() if len(kinds) == 1 else None


def check_hashing(source: SourceFile) -> Iterator[Problem]:
    """Find unhashable set elements and dictionary keys.

    :param source: a file with a correct syntax
    :return: the problems
    """
    module = _read_scope(source.tree, _Scope())
    shared = _Scope({name: (kind, 0) for name, (kind, _) in module.variables.items()})
    functions = [node for node in ast.walk(source.tree) if isinstance(node, _FUNCTIONS)]
    returns = {node.name: _return_kind(node, shared) for node in functions}
    for tree in (source.tree, *functions):
        scope = _read_scope(tree, _Scope(shared.variables, returns))
        for node in _walk_scope(tree):
            for value, place in _hashed_values(node, scope):
                kind = scope.kind(value)
                if kind is not None:
                    message = f"{_FRENCH[kind]} ne peut pas être {place}"
                    yield Problem(message, source.name, value.lineno, source.line(value.lineno))


def _walk_scope(scope: ast.AST) -> Iterator[ast.AST]:
    """Walk a module or a function without entering the functions defined inside."""
    pending = list(ast.iter_child_nodes(scope))
    while pending:
        node = pending.pop(0)
        yield node
        if not isinstance(node, (*_FUNCTIONS, ast.ClassDef, ast.Lambda)):
            pending.extend(ast.iter_child_nodes(node))


def _hashed_values(node: ast.AST, scope: _Scope) -> Iterator[tuple[ast.expr, str]]:
    """List the expressions that must be hashable in a node."""
    match node:
        case ast.Set(elts=items):
            yield from ((item, _ELEMENT) for item in items)
        case ast.SetComp(elt=item):
            yield item, _ELEMENT
        case ast.Dict(keys=keys):
            yield from ((key, _KEY) for key in keys if key is not None)
        case ast.DictComp(key=key, value=ast.expr()):
            yield key, _KEY
        case ast.Subscript(value=value, slice=key, ctx=ast.Store()):
            if scope.kind(value) == "dict":
                yield key, _KEY
        case ast.Call(func=ast.Attribute(value=value, attr=name), args=[first, *_]):
            methods, place = _METHODS.get(scope.kind(value), ((), ""))
            if name in methods:
                yield first, place


def _read_scope(tree: ast.AST, outer: _Scope) -> _Scope:
    """Find the variables that only ever receive lists, dictionaries or sets."""
    scope = _Scope(outer.variables, outer.returns)
    for _ in range(_PASSES):  # A variable can be the copy of another one.
        received = _received_kinds(tree, scope)
        variables = {k: v for k, v in outer.variables.items() if k not in received}
        for name, kinds in received.items():
            first = kinds[0][0]
            if first is not None and all(kind == first for kind, _ in kinds):
                variables[name] = first, min(line for _, line in kinds)
        scope = _Scope(variables, outer.returns)
    return scope


def _received_kinds(tree: ast.AST, scope: _Scope) -> dict[str, list[tuple[str | None, int]]]:
    """List what each variable of a scope receives: a kind and a line."""
    kinds, local = {}, set()
    for node in _walk_scope(tree):
        match node:
            case ast.Assign(targets=targets, value=value):
                kinds.update((id(target), scope.kind(value)) for target in targets)
            case ast.NamedExpr(target=target, value=value):
                kinds[id(target)] = scope.kind(value)
            case ast.AnnAssign(target=target, annotation=annotation, value=value):
                kind = _annotated_kind(annotation)
                kinds[id(target)] = kind or (scope.kind(value) if value else None)
            case ast.For(target=target, iter=items) | ast.comprehension(target=target, iter=items):
                kinds[id(target)] = scope.element_kind(items)
                if isinstance(node, ast.comprehension):
                    local.add(id(target))
    kept = {id(node.target) for node in _walk_scope(tree) if isinstance(node, ast.AugAssign)}
    received = _parameter_kinds(tree) if isinstance(tree, _FUNCTIONS) else {}
    for node in _walk_scope(tree):
        if isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Load):
            if id(node) not in kept:
                line = 0 if id(node) in local else node.lineno
                received.setdefault(node.id, []).append((kinds.get(id(node)), line))
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            for name in node.names:
                received.setdefault(name, []).append((None, node.lineno))
    return received


def _parameter_kinds(function: ast.FunctionDef) -> dict[str, list[tuple[str | None, int]]]:
    """Kinds of the parameters, except those that receive another value at once."""
    replaced = {
        target.id
        for node in function.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    received = {}
    for node in ast.walk(function.args):
        if isinstance(node, ast.arg):
            kind = "dict" if node is function.args.kwarg else _annotated_kind(node.annotation)
            if kind is not None or node.arg not in replaced:
                received[node.arg] = [(kind, 0)]
    return received


def _return_kind(function: ast.FunctionDef, module: _Scope) -> str | None:
    if function.returns is not None:
        return _annotated_kind(function.returns)
    scope = _read_scope(function, module)
    nodes = list(_walk_scope(function))
    if any(isinstance(node, (ast.Yield, ast.YieldFrom)) for node in nodes):
        return None
    values = [node.value for node in nodes if isinstance(node, ast.Return)]
    kinds = {scope.kind(value) if value else None for value in values}
    return kinds.pop() if len(kinds) == 1 else None


def _annotated_kind(annotation: ast.expr | None) -> str | None:
    if isinstance(annotation, ast.Subscript):
        annotation = annotation.value
    if isinstance(annotation, ast.Name) and annotation.id in _ANNOTATIONS:
        return annotation.id.lower()
    return None
