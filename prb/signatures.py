"""Checking that the functions of the statement exist, with their exact signature.

A missing or misnamed function does not make a submission inadmissible: files may even be
empty. It is simply considered absent, so its tests fail while the others still run.
"""

import ast
import difflib

from prb.model import PROGRAM, Exercise, FunctionSpec
from prb.sources import Problem, SourceFile


def check_functions(exercise: Exercise, sources: dict[str, SourceFile]) -> dict[str, Problem]:
    """Find what cannot be tested because it is missing or has another signature.

    :param exercise: the exercise
    :param sources: the student's files, all with a correct syntax
    :return: the reasons, indexed by the target of the tests that cannot run
    """
    missing = {}
    for function in exercise.functions:
        problem = _check_function(function, sources)
        if problem:
            missing[function.target] = problem
    if exercise.main:
        problem = _check_main(exercise.main, sources[exercise.main])
        if problem:
            missing[PROGRAM] = problem
    return missing


def find_function(tree: ast.Module, name: str) -> ast.FunctionDef | None:
    """Find a function defined at the top level of a module.

    :param tree: the parsed module
    :param name: the function name
    :return: the last definition, or None
    """
    matches = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name]
    return matches[-1] if matches else None


def _check_function(function: FunctionSpec, sources: dict[str, SourceFile]) -> Problem | None:
    source = sources[function.file]
    found = find_function(source.tree, function.name)
    if found is None:
        return _describe_missing(function, source, sources)
    expected, obtained = _parameters(function.node), _parameters(found)
    if _same_parameters(expected, obtained):
        return None
    message = (
        f"signature de {function.name} : l'énoncé demande "
        f"({', '.join(expected)}), tu as ({', '.join(obtained)})"
    )
    return Problem(message, source.name, found.lineno)


def _check_main(main: str, source: SourceFile) -> Problem | None:
    found = find_function(source.tree, "main")
    if found is None:
        return Problem(f"fonction main() absente de {main}", main)
    if _parameters(found):
        return Problem("main() ne doit pas avoir de paramètre", main, found.lineno)
    return None


def _describe_missing(
    function: FunctionSpec, source: SourceFile, sources: dict[str, SourceFile]
) -> Problem:
    message = f"fonction {function.name} absente de {source.name}"
    for other in sources.values():
        if other is not source and find_function(other.tree, function.name):
            return Problem(f"{message} : tu l'as définie dans {other.name}", source.name)
    for node in ast.walk(source.tree):
        if isinstance(node, ast.FunctionDef) and node.name == function.name:
            return Problem(f"{message} : elle est imbriquée", source.name, node.lineno)
    names = [node.name for node in source.tree.body if isinstance(node, ast.FunctionDef)]
    close = difflib.get_close_matches(function.name, names, n=1, cutoff=0.6)
    if close:
        message += f" : tu as défini {close[0]}"
    return Problem(message, source.name)


def _parameters(node: ast.FunctionDef) -> list[str]:
    """Write the parameters without their annotations."""
    arguments = node.args
    positional = [*arguments.posonlyargs, *arguments.args]
    defaults = [None] * (len(positional) - len(arguments.defaults)) + arguments.defaults
    result = [_parameter(arg, value) for arg, value in zip(positional, defaults, strict=True)]
    if arguments.vararg:
        result.append(f"*{arguments.vararg.arg}")
    elif arguments.kwonlyargs:
        result.append("*")
    for arg, value in zip(arguments.kwonlyargs, arguments.kw_defaults, strict=True):
        result.append(_parameter(arg, value))
    if arguments.kwarg:
        result.append(f"**{arguments.kwarg.arg}")
    return result


def _same_parameters(expected: list[str], obtained: list[str]) -> bool:
    """Compare parameters. A default value written « ... » stands for any default value."""
    if len(expected) != len(obtained):
        return False
    return all(
        found.startswith(wanted[:-3]) if wanted.endswith("=...") else found == wanted
        for wanted, found in zip(expected, obtained, strict=True)
    )


def _parameter(arg: ast.arg, default: ast.expr | None) -> str:
    return arg.arg if default is None else f"{arg.arg}={ast.unparse(default)}"
