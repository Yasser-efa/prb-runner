"""Detection of invalid regular expressions.

PyCharm reads the patterns given to the functions of ``re`` and shows their mistakes as errors.
"""

import ast
import re
import warnings
from collections.abc import Iterator

from prb.sources import Problem, SourceFile

_FUNCTIONS = {
    "compile", "search", "match", "prefixmatch", "fullmatch", "split", "findall", "finditer",
    "sub", "subn",
}  # fmt: skip
_VERBOSE = {"X", "VERBOSE"}
_FRENCH = (
    (r"unterminated character set", r"crochet [ non fermé"),
    (r"missing \), unterminated subpattern", r"parenthèse ( non fermée"),
    (r"unbalanced parenthesis", r"parenthèse ) en trop"),
    (r"nothing to repeat", r"répétition sans rien devant"),
    (r"multiple repeat", r"deux répétitions à la suite"),
    (r"min repeat greater than max repeat", r"répétition dont le minimum dépasse le maximum"),
    (r"bad escape \(end of pattern\)", r"barre \\ seule à la fin"),
    (r"bad escape (.+)", r"échappement inconnu \1"),
    (r"bad character range (.+)", r"intervalle incorrect \1"),
    (r"(?:invalid group reference|unknown group name) (.+)", r"le groupe \1 n'existe pas"),
    (r"redefinition of group name ('.+?').*", r"deux groupes nommés \1"),
    (r"look-behind requires.*", r"(?<=…) doit avoir une longueur fixe"),
)


def check_patterns(source: SourceFile) -> Iterator[Problem]:
    """Find the regular expressions that Python refuses.

    :param source: a file with a correct syntax
    :return: the problems
    """
    modules, functions = _imported_names(source.tree)
    for node in ast.walk(source.tree):
        if isinstance(node, ast.Call) and _is_re_function(node.func, modules, functions):
            pattern = _pattern(node)
            text = _literal_text(pattern) if pattern is not None else None
            error = _error(text, _is_verbose(node)) if text is not None else None
            if error is not None:
                message = f"expression régulière incorrecte : {error}"
                line = pattern.lineno
                yield Problem(message, source.name, line, source.line(line))


def _imported_names(tree: ast.Module) -> tuple[set[str], set[str]]:
    """Names given to the module ``re`` and to its functions."""
    modules, functions = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.asname or "re" for alias in node.names if alias.name == "re")
        elif isinstance(node, ast.ImportFrom) and node.module == "re" and node.level == 0:
            functions.update(
                alias.asname or alias.name for alias in node.names if alias.name in _FUNCTIONS
            )
    return modules, functions


def _is_re_function(node: ast.expr, modules: set[str], functions: set[str]) -> bool:
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        return node.value.id in modules and node.attr in _FUNCTIONS
    return isinstance(node, ast.Name) and node.id in functions


def _pattern(call: ast.Call) -> ast.expr | None:
    if call.args:
        return call.args[0]
    return next((item.value for item in call.keywords if item.arg == "pattern"), None)


def _literal_text(node: ast.expr) -> str | bytes | None:
    """Read a text written in the code, None if it is computed."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (str, bytes)):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        parts = [node.left, node.right]
    elif isinstance(node, ast.JoinedStr):
        parts = node.values
    else:
        return None
    texts = [_literal_text(part) for part in parts]
    return "".join(texts) if all(isinstance(text, str) for text in texts) else None


def _is_verbose(call: ast.Call) -> bool:
    values = [*call.args[1:], *(item.value for item in call.keywords)]
    names = [node for value in values for node in ast.walk(value)]
    return any(
        (isinstance(node, ast.Attribute) and node.attr in _VERBOSE)
        or (isinstance(node, ast.Name) and node.id in _VERBOSE)
        for node in names
    )


def _error(text: str | bytes, verbose: bool) -> str | None:
    """Explain in French why Python refuses a pattern, None if it is correct."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            re.compile(text, re.VERBOSE if verbose else 0)
    except re.PatternError as error:
        for english, french in _FRENCH:
            match = re.fullmatch(english, error.msg)
            if match:
                return match.expand(french)
        return error.msg
    except (OverflowError, RecursionError) as error:
        return str(error)
    return None
