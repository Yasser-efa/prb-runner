"""Checking of Sphinx docstrings.

Type annotations in the header can replace ``:type:`` and ``:rtype:``.
"""

import ast
import re
from collections.abc import Iterator
from dataclasses import dataclass, field

from prb.sources import Problem, SourceFile

GROUP = "Documentation"
_FIELD = re.compile(r"^\s*:(?P<tag>\w+)(?:\s+(?P<target>[^:]*?))?\s*:(?P<text>.*)$")
_PARAM_TAGS = {"param", "parameter", "arg", "argument"}
_RETURN_TAGS = {"return", "returns"}
_FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)


@dataclass
class _Docstring:
    """Content of a Sphinx docstring."""

    description: str = ""
    params: dict[str, str] = field(default_factory=dict)
    types: dict[str, str] = field(default_factory=dict)
    returns: str | None = None
    rtype: str | None = None
    unknown_tags: list[str] = field(default_factory=list)


def check_docstrings(source: SourceFile) -> Iterator[Problem]:
    """Check the docstring of every function of a file.

    :param source: a file with a correct syntax
    :return: the remarks
    """
    for node in ast.walk(source.tree):
        if isinstance(node, _FUNCTIONS):
            for message in _check_function(node):
                yield Problem(f"{node.name} : {message}", source.name, node.lineno, group=GROUP)


def _check_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> Iterator[str]:
    text = ast.get_docstring(node)
    if not text:
        yield "docstring absente"
        return
    doc = _parse(text)
    if not doc.description:
        yield "description absente de la docstring"
    yield from _check_parameters(node, doc)
    yield from _check_return(node, doc)
    for tag in doc.unknown_tags:
        yield f"étiquette Sphinx inconnue (:{tag}:)"


def _check_parameters(node: ast.FunctionDef | ast.AsyncFunctionDef, doc: _Docstring):
    expected = _parameters(node)
    for name, annotated in expected.items():
        if name not in doc.params:
            yield f"« :param {name}: » absent"
        elif not doc.params[name]:
            yield f"« :param {name}: » sans description"
        if not annotated and not doc.types.get(name):
            yield f"type de « {name} » absent (annotation ou :type {name}:)"
    for name in doc.params.keys() | doc.types.keys():
        if name not in expected:
            yield f"« {name} » est documenté mais n'est pas un paramètre"


def _check_return(node: ast.FunctionDef | ast.AsyncFunctionDef, doc: _Docstring):
    if not _returns_value(node):
        return
    if doc.returns is None:
        yield "« :return: » absent"
    elif not doc.returns:
        yield "« :return: » sans description"
    if node.returns is None and not doc.rtype:
        yield "type de la valeur renvoyée absent (annotation -> ou :rtype:)"


def _parameters(node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, bool]:
    """Map each parameter to whether it is annotated."""
    arguments = node.args
    every = [*arguments.posonlyargs, *arguments.args, *arguments.kwonlyargs]
    every += [arg for arg in (arguments.vararg, arguments.kwarg) if arg]
    return {
        arg.arg: arg.annotation is not None for arg in every if arg.arg not in ("self", "cls")
    }


def _returns_value(node: ast.AST) -> bool:
    pending = list(ast.iter_child_nodes(node))
    while pending:
        child = pending.pop()
        if isinstance(child, (ast.Yield, ast.YieldFrom)):
            return True
        if isinstance(child, ast.Return) and child.value is not None:
            if not (isinstance(child.value, ast.Constant) and child.value.value is None):
                return True
        if not isinstance(child, (*_FUNCTIONS, ast.Lambda, ast.ClassDef)):
            pending.extend(ast.iter_child_nodes(child))
    return False


def _parse(text: str) -> _Docstring:
    doc = _Docstring()
    description: list[str] = []
    fields: list[list[str]] = []
    for line in text.splitlines():
        match = _FIELD.match(line)
        if match:
            fields.append([match["tag"], (match["target"] or "").strip(), match["text"].strip()])
        elif fields:
            fields[-1][2] = f"{fields[-1][2]} {line.strip()}".strip()
        else:
            description.append(line.strip())
    doc.description = " ".join(description).strip()
    for tag, target, content in fields:
        _store(doc, tag, target, content)
    return doc


def _store(doc: _Docstring, tag: str, target: str, content: str) -> None:
    if tag in _PARAM_TAGS:
        # « :param int age: … » gives the type and the name at once.
        *kind, name = target.split() or [""]
        name = name.lstrip("*")
        doc.params[name] = content
        if kind:
            doc.types[name] = " ".join(kind)
    elif tag == "type":
        doc.types[target.lstrip("*")] = content
    elif tag in _RETURN_TAGS:
        doc.returns = content
    elif tag == "rtype":
        doc.rtype = content
    elif tag not in ("raise", "raises", "except", "var", "ivar", "cvar", "meta"):
        doc.unknown_tags.append(tag)
