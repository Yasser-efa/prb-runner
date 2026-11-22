"""Detection of ``for`` variables that are used again after their loop.

The names of each scope are listed in the order in which Python evaluates them. Using a
loop variable after its loop is reported unless it receives a new value first.
"""

import ast
from collections.abc import Iterator
from dataclasses import dataclass, field

from prb.sources import Problem, SourceFile

GROUP = "Bonnes pratiques"
_FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)
_Branch = tuple[tuple[int, str], ...]


@dataclass
class _Event:
    """A name being read or written."""

    name: str
    line: int
    is_read: bool
    branch: _Branch


@dataclass
class _Loop:
    """A ``for`` loop and the events that follow it."""

    names: set[str]
    line: int
    end: int = 0
    branch: _Branch = ()
    nested_in: list[_Loop] = field(default_factory=list)


def check_loop_variables(source: SourceFile) -> Iterator[Problem]:
    """Report loop variables that are used after the loop or reused by a nested loop.

    :param source: a file with a correct syntax
    :return: the remarks
    """
    scopes = [source.tree] + [n for n in ast.walk(source.tree) if isinstance(n, _FUNCTIONS)]
    for scope in scopes:
        yield from _check_scope(scope, source)


def _check_scope(scope: ast.Module | ast.FunctionDef, source: SourceFile) -> Iterator[Problem]:
    collector = _Collector()
    for statement in scope.body:
        collector.visit(statement)
    reported = set()
    for loop in collector.loops:
        for name in sorted(loop.names - {"_"}):
            line = _use_after(name, loop, collector.events)
            message = f"variable de boucle « {name} » utilisée après la boucle (ligne {loop.line})"
            if line is None and any(name in outer.names for outer in loop.nested_in):
                line = loop.line
                message = f"variable de boucle « {name} » déjà utilisée par la boucle extérieure"
            if line is not None and (name, line) not in reported:
                reported.add((name, line))
                yield Problem(message, source.name, line, source.line(line), GROUP)


def _use_after(name: str, loop: _Loop, events: list[_Event]) -> int | None:
    for event in events[loop.end :]:
        if event.name != name or _exclusive(loop.branch, event.branch):
            continue
        return event.line if event.is_read else None
    return None


def _exclusive(first: _Branch, second: _Branch) -> bool:
    """Tell whether two places are in opposite branches of the same test."""
    sides = dict(first)
    return any(node in sides and sides[node] != side for node, side in second)


class _Collector(ast.NodeVisitor):
    """Lists reads and writes of names in evaluation order, in one scope."""

    def __init__(self) -> None:
        self.events: list[_Event] = []
        self.loops: list[_Loop] = []
        self.branch: _Branch = ()
        self.hidden: list[set[str]] = []
        self.open_loops: list[_Loop] = []

    def _add(self, name: str, node: ast.AST, is_read: bool) -> None:
        if not any(name in names for names in self.hidden):
            self.events.append(_Event(name, node.lineno, is_read, self.branch))

    def visit_Name(self, node: ast.Name) -> None:  # noqa: N802
        self._add(node.id, node, isinstance(node.ctx, ast.Load))

    def visit_Assign(self, node: ast.Assign) -> None:  # noqa: N802
        self.visit(node.value)
        for target in node.targets:
            self.visit(target)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:  # noqa: N802
        if node.value is not None:
            self.visit(node.value)
            self.visit(node.target)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:  # noqa: N802
        if isinstance(node.target, ast.Name):
            self._add(node.target.id, node.target, is_read=True)
        self.visit(node.value)
        self.visit(node.target)

    def visit_NamedExpr(self, node: ast.NamedExpr) -> None:  # noqa: N802
        self.visit(node.value)
        self.visit(node.target)

    def visit_For(self, node: ast.For) -> None:  # noqa: N802
        self.visit(node.iter)
        self.visit(node.target)
        names = {n.id for n in ast.walk(node.target) if isinstance(n, ast.Name)}
        loop = _Loop(names, node.lineno, branch=self.branch, nested_in=list(self.open_loops))
        self.loops.append(loop)
        self.open_loops.append(loop)
        for statement in node.body:
            self.visit(statement)
        self.open_loops.pop()
        for statement in node.orelse:
            self.visit(statement)
        loop.end = len(self.events)

    def visit_If(self, node: ast.If) -> None:  # noqa: N802
        self.visit(node.test)
        self._visit_branch(node, "body", node.body)
        self._visit_branch(node, "orelse", node.orelse)

    def visit_Match(self, node: ast.Match) -> None:  # noqa: N802
        self.visit(node.subject)
        for number, case in enumerate(node.cases):
            self._visit_branch(node, str(number), [case])

    def _visit_branch(self, node: ast.AST, side: str, body: list[ast.AST]) -> None:
        saved = self.branch
        self.branch = (*saved, (id(node), side))
        for child in body:
            self.visit(child)
        self.branch = saved

    def _visit_function(self, node: ast.FunctionDef) -> None:
        for decorator in node.decorator_list:
            self.visit(decorator)
        for default in [*node.args.defaults, *node.args.kw_defaults]:
            if default is not None:
                self.visit(default)

    visit_FunctionDef = _visit_function  # noqa: N815
    visit_AsyncFunctionDef = _visit_function  # noqa: N815

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        """Ignore classes: they are not part of the course."""

    def visit_Lambda(self, node: ast.Lambda) -> None:  # noqa: N802
        self.hidden.append({arg.arg for arg in node.args.args})
        self.visit(node.body)
        self.hidden.pop()

    def _visit_comprehension(self, node: ast.ListComp | ast.DictComp) -> None:
        self.visit(node.generators[0].iter)
        names = {
            n.id
            for generator in node.generators
            for n in ast.walk(generator.target)
            if isinstance(n, ast.Name)
        }
        self.hidden.append(names)
        for position, generator in enumerate(node.generators):
            if position > 0:
                self.visit(generator.iter)
            for condition in generator.ifs:
                self.visit(condition)
        if isinstance(node, ast.DictComp):
            self.visit(node.key)
            self.visit(node.value)
        else:
            self.visit(node.elt)
        self.hidden.pop()

    visit_ListComp = _visit_comprehension  # noqa: N815
    visit_SetComp = _visit_comprehension  # noqa: N815
    visit_DictComp = _visit_comprehension  # noqa: N815
    visit_GeneratorExp = _visit_comprehension  # noqa: N815
