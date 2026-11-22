"""Step 1 of the verdict: would the submission be accepted at all?"""

import ast
import difflib
from pathlib import Path, PurePosixPath

from prb.imports import check_imports
from prb.linting import BLOCKING_RULES, lint
from prb.model import Exercise, FunctionSpec
from prb.sources import Problem, SourceFile, list_files


def check_admissibility(
    exercise: Exercise, folder: Path, sources: dict[str, SourceFile]
) -> list[Problem]:
    """Look for what makes a submission worth zero at the exam.

    :param exercise: the exercise
    :param folder: the student's folder
    :param sources: the Python files of that folder
    :return: the blocking problems, empty if the submission is admissible
    """
    problems = _check_layout(exercise, folder)
    problems += _check_provided(exercise, folder)
    problems += [source.error for source in sources.values() if source.error]
    problems += _check_names(folder, sources)
    problems += check_imports(sources)
    for function in exercise.functions:
        problems += _check_function(function, sources)
    if exercise.main:
        problems += _check_main(exercise.main, sources)
    return problems


def unexpected_files(exercise: Exercise, folder: Path) -> list[Problem]:
    """Find Python files that the statement does not mention.

    :param exercise: the exercise
    :param folder: the student's folder
    :return: one remark per extra file
    """
    expected = {name.casefold() for name in (*exercise.files, *exercise.provided_names)}
    return [
        Problem("fichier non demandé : retire-le avant de créer le ZIP", name)
        for name in list_files(folder)
        if name.endswith(".py") and name.casefold() not in expected
    ]


def _check_layout(exercise: Exercise, folder: Path) -> list[Problem]:
    present = [name for name in list_files(folder) if name not in exercise.provided_names]
    if not present:
        return [Problem(f"le dossier mes_solutions/{exercise.id}/ est vide")]
    problems = []
    for name in exercise.files:
        if name not in present:
            problems.append(Problem(_describe_missing(name, present, exercise.files)))
    return problems


def _check_provided(exercise: Exercise, folder: Path) -> list[Problem]:
    """Check that the provided files are there, and intact when they must be."""
    present = set(list_files(folder))
    problems = []
    for file in exercise.provided:
        if file.name not in present:
            message = "fichier fourni manquant : relance du_jour pour le recopier"
            problems.append(Problem(message, file.name))
        elif not file.editable and not file.matches((folder / file.name).read_bytes()):
            message = "fichier fourni modifié : c'est interdit (supprime-le et relance du_jour)"
            problems.append(Problem(message, file.name))
    return problems


def _describe_missing(name: str, present: list[str], expected: tuple[str, ...]) -> str:
    spare = [other for other in present if other not in expected]
    for other in spare:
        if other.casefold() == name.casefold():
            return f"« {other} » trouvé, mais l'énoncé demande « {name} » (majuscules comprises)"
    path = PurePosixPath(name)
    if path.name == "__init__.py":
        return f"il manque {name} : « {path.parent} » doit être un package"
    for other in spare:
        if PurePosixPath(other).name.casefold() == path.name.casefold():
            return f"« {other} » est mal placé : l'énoncé demande « {name} »"
    close = difflib.get_close_matches(name, spare, n=1, cutoff=0.75)
    suffix = f" (tu as « {close[0]} »)" if close else ""
    return f"fichier manquant : {name}{suffix}"


def _check_names(folder: Path, sources: dict[str, SourceFile]) -> list[Problem]:
    files = [name for name, source in sources.items() if source.tree is not None]
    problems = []
    for message in lint(folder, files, BLOCKING_RULES):
        source_line = sources[message.file].line(message.line)
        problems.append(Problem(message.message, message.file, message.line, source_line))
    return problems


def _check_function(function: FunctionSpec, sources: dict[str, SourceFile]) -> list[Problem]:
    source = sources.get(function.file)
    if source is None or source.tree is None:
        return []
    found = find_function(source.tree, function.name)
    if found is None:
        return [_describe_missing_function(function, source, sources)]
    expected, obtained = _parameters(function.node), _parameters(found)
    if not _same_parameters(expected, obtained):
        message = (
            f"signature de {function.name} : l'énoncé demande "
            f"({', '.join(expected)}), tu as ({', '.join(obtained)})"
        )
        return [Problem(message, source.name, found.lineno)]
    return []


def _check_main(main: str, sources: dict[str, SourceFile]) -> list[Problem]:
    source = sources.get(main)
    if source is None or source.tree is None:
        return []
    found = find_function(source.tree, "main")
    if found is None:
        return [Problem(f"fonction main() absente de {main}", main)]
    if _parameters(found):
        return [Problem("main() ne doit pas avoir de paramètre", main, found.lineno)]
    return []


def find_function(tree: ast.Module, name: str) -> ast.FunctionDef | None:
    """Find a function defined at the top level of a module.

    :param tree: the parsed module
    :param name: the function name
    :return: the last definition, or None
    """
    matches = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name]
    return matches[-1] if matches else None


def _describe_missing_function(
    function: FunctionSpec, source: SourceFile, sources: dict[str, SourceFile]
) -> Problem:
    message = f"fonction {function.name} absente de {source.name}"
    for other in sources.values():
        if other is not source and other.tree and find_function(other.tree, function.name):
            return Problem(f"{message} : tu l'as définie dans {other.name}", source.name)
    names = [node.name for node in source.tree.body if isinstance(node, ast.FunctionDef)]
    for node in ast.walk(source.tree):
        if isinstance(node, ast.FunctionDef) and node.name == function.name:
            return Problem(f"{message} : elle est imbriquée", source.name, node.lineno)
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
