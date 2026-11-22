"""Step 2 of the verdict: constraints of the statement, checked on the syntax tree."""

import ast
from collections.abc import Iterator

from prb.constructs import CONSTRUCTS
from prb.model import ConstraintSet, Exercise
from prb.signatures import find_function
from prb.sources import Problem, SourceFile

_Located = tuple[SourceFile, ast.AST]


def check_constraints(exercise: Exercise, sources: dict[str, SourceFile]) -> list[Problem]:
    """Check every constraint of an exercise.

    :param exercise: the exercise
    :param sources: the student's files, all with a correct syntax
    :return: the constraints that are not respected
    """
    problems = []
    for constraint in exercise.constraints:
        scope = _scope(exercise, constraint, sources)
        if not scope:
            continue  # The function is absent, which is reported by the tests.
        place = f" dans {constraint.function}" if constraint.function else ""
        problems += _check_forbidden(constraint, scope, place)
        problems += _check_required(constraint, scope, place)
        problems += _check_forbidden_functions(constraint, scope, place)
        problems += _check_forbidden_modules(constraint, scope, place)
        problems += _check_required_modules(constraint, scope, place)
        problems += _check_required_calls(constraint, scope, place)
    return problems


def _scope(
    exercise: Exercise, constraint: ConstraintSet, sources: dict[str, SourceFile]
) -> list[_Located]:
    """Trees on which a constraint applies."""
    if constraint.function is None:
        return [(source, source.tree) for source in sources.values() if source.tree]
    spec = next(item for item in exercise.functions if item.name == constraint.function)
    source = sources[spec.file]
    function = find_function(source.tree, spec.name)
    return [(source, function)] if function else []


def _check_forbidden(
    constraint: ConstraintSet, scope: list[_Located], place: str
) -> Iterator[Problem]:
    for name in constraint.forbidden:
        for source, tree in scope:
            for node in ast.walk(tree):
                if CONSTRUCTS[name](node):
                    yield _problem(f"« {name} » est interdit{place}", source, node)


def _check_required(
    constraint: ConstraintSet, scope: list[_Located], place: str
) -> Iterator[Problem]:
    for name in constraint.required:
        nodes = (node for _, tree in scope for node in ast.walk(tree))
        if not any(CONSTRUCTS[name](node) for node in nodes):
            yield Problem(f"l'énoncé impose d'utiliser « {name} »{place}")


def _check_forbidden_functions(
    constraint: ConstraintSet, scope: list[_Located], place: str
) -> Iterator[Problem]:
    for name in constraint.forbidden_functions:
        for source, tree in scope:
            for node in _uses(tree, name, source.tree):
                label = f"la méthode {name}()" if name.startswith(".") else f"{name}()"
                yield _problem(f"{label} est interdit{place}", source, node)


def _uses(tree: ast.AST, name: str, module: ast.Module) -> Iterator[ast.AST]:
    """Find the uses of a function, or of a method when the name starts with a dot."""
    if name.startswith("."):
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr == name[1:]:
                yield node
        return
    harmless = _annotation_nodes(tree) | _isinstance_types(tree)
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and node.id == name:
            if id(node) not in harmless:
                yield node
        elif isinstance(node, ast.Attribute) and node.attr == name:
            # tables.calculs.table, builtins.int
            if isinstance(node.value, (ast.Name, ast.Attribute)) and _is_module(module, node.value):
                yield node


def _is_module(module: ast.Module, node: ast.expr) -> bool:
    """Tell whether an expression is something imported by the module."""
    while isinstance(node, ast.Attribute):
        node = node.value
    if not isinstance(node, ast.Name):
        return False
    imported = {"builtins"}
    for other in ast.walk(module):
        if isinstance(other, (ast.Import, ast.ImportFrom)):
            imported.update((alias.asname or alias.name).split(".")[0] for alias in other.names)
    return node.id in imported


def _annotation_nodes(tree: ast.AST) -> set[int]:
    """Identify the nodes inside type annotations: ``-> int`` is not a call."""
    annotations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.arg):
            annotations.append(node.annotation)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            annotations.append(node.returns)
        elif isinstance(node, ast.AnnAssign):
            annotations.append(node.annotation)
        elif isinstance(node, ast.TypeAlias):
            annotations.append(node.value)
    return {id(child) for root in annotations if root is not None for child in ast.walk(root)}


def _isinstance_types(tree: ast.AST) -> set[int]:
    result = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in ("isinstance", "issubclass")
        ):
            for argument in node.args[1:]:
                result.update(id(child) for child in ast.walk(argument))
    return result


def _check_forbidden_modules(
    constraint: ConstraintSet, scope: list[_Located], place: str
) -> Iterator[Problem]:
    for name in constraint.forbidden_modules:
        for source, tree in scope:
            for node in _imports_of(tree, name):
                yield _problem(f"le module {name} est interdit{place}", source, node)


def _check_required_modules(
    constraint: ConstraintSet, scope: list[_Located], place: str
) -> Iterator[Problem]:
    for name in constraint.required_modules:
        if not any(True for _, tree in scope for _ in _imports_of(tree, name)):
            yield Problem(f"l'énoncé impose d'utiliser le module {name}{place}")


def _imports_of(tree: ast.AST, name: str) -> Iterator[ast.AST]:
    """Find the imports of a module or of something inside it."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            modules = [node.module or ""]
        else:
            continue
        if any(module == name or module.startswith(f"{name}.") for module in modules):
            yield node


def _check_required_calls(
    constraint: ConstraintSet, scope: list[_Located], place: str
) -> Iterator[Problem]:
    for name in constraint.required_calls:
        if not any(_calls(tree, name) for _, tree in scope):
            yield Problem(f"l'énoncé impose d'utiliser la fonction {name}{place}")


def _calls(tree: ast.AST, name: str) -> bool:
    """Look for a call to a function, recursive calls excluded."""
    inside = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            inside.update(id(child) for child in ast.walk(node))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and id(node) not in inside:
            target = node.func
            called = target.id if isinstance(target, ast.Name) else getattr(target, "attr", None)
            if called == name:
                return True
        # A function given to another one (map, sorted…) counts as used.
        if isinstance(node, ast.Call):
            values = [*node.args, *(keyword.value for keyword in node.keywords)]
            if any(isinstance(v, ast.Name) and v.id == name for v in values):
                return True
    return False


def _problem(message: str, source: SourceFile, node: ast.AST) -> Problem:
    return Problem(message, source.name, node.lineno, source.line(node.lineno))
