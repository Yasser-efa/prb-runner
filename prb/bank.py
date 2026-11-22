"""Reading of the exercise bank (TOML and Markdown files)."""

import ast
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from prb.constructs import CONSTRUCTS
from prb.literals import Call, LiteralError, parse_call, parse_literal
from prb.paths import Paths

DEFAULT_MINUTES = 40
DEFAULT_TIMEOUT = 2.0
KINDS = ("fonction", "programme")
_ID_PATTERN = re.compile(r"[a-z][a-z0-9_]*")


class BankError(Exception):
    """A file of the bank is missing or badly formatted."""


@dataclass(frozen=True)
class FunctionSpec:
    """A function required by an exercise."""

    module: str
    name: str
    signature: str
    node: ast.FunctionDef
    preserve_arguments: bool = False

    @property
    def file(self) -> str:
        """Path of the file that must define the function."""
        return self.module.replace(".", "/") + ".py"

    @property
    def returns_float(self) -> bool:
        """Tell whether the announced return type mentions float."""
        return self.node.returns is not None and "float" in ast.unparse(self.node.returns)


@dataclass(frozen=True)
class ConstraintSet:
    """Constraints on the whole code (``function`` is None) or on one function."""

    function: str | None = None
    forbidden: tuple[str, ...] = ()
    required: tuple[str, ...] = ()
    forbidden_functions: tuple[str, ...] = ()
    forbidden_modules: tuple[str, ...] = ()
    required_calls: tuple[str, ...] = ()


@dataclass(frozen=True)
class Case:
    """One execution of the code: a function call, or the whole program."""

    label: str
    function: FunctionSpec | None = None
    args: tuple = ()
    kwargs: tuple[tuple[str, object], ...] = ()
    stdin: tuple[str, ...] = ()
    has_value: bool = False
    value: object = None
    output: str | None = None
    theme: str | None = None

    @property
    def is_program(self) -> bool:
        """Tell whether the case runs the whole program."""
        return self.function is None


@dataclass(frozen=True)
class Exercise:
    """Everything the tool knows about one exercise."""

    id: str
    title: str
    reference: str
    kind: str
    minutes: int
    timeout: float
    files: tuple[str, ...]
    main: str | None
    functions: tuple[FunctionSpec, ...]
    constraints: tuple[ConstraintSet, ...]
    statement: str
    visible_cases: tuple[Case, ...]
    hidden_cases: tuple[Case, ...]
    hints: tuple[str, ...]
    reference_folder: Path


def load_order(paths: Paths) -> list[str]:
    """Read the order in which new exercises are proposed.

    :param paths: the project folders
    :return: the identifiers, first exercise first
    """
    data = _read_toml(paths.exercises / "ordre.toml")
    _check_keys(data, {"ordre"}, "ordre.toml")
    order = list(_strings(data, "ordre", "ordre.toml"))
    duplicates = {name for name in order if order.count(name) > 1}
    if duplicates:
        raise BankError(f"ordre.toml : identifiants en double ({', '.join(sorted(duplicates))})")
    return order


def load_bank(paths: Paths) -> list[Exercise]:
    """Load every exercise, in the order of ``ordre.toml``.

    :param paths: the project folders
    :return: the exercises
    """
    order = load_order(paths)
    present = {path.parent.name for path in paths.exercises.glob("*/exercice.toml")}
    forgotten = present - set(order)
    if forgotten:
        raise BankError(f"ordre.toml : il manque {', '.join(sorted(forgotten))}")
    return [load_exercise(paths, exercise_id) for exercise_id in order]


def load_exercise(paths: Paths, exercise_id: str) -> Exercise:
    """Load one exercise, public and private parts.

    :param paths: the project folders
    :param exercise_id: the name of the exercise folder
    :return: the exercise
    :raises BankError: if a file is missing or badly formatted
    """
    folder = paths.exercises / exercise_id
    if not _ID_PATTERN.fullmatch(exercise_id) or not (folder / "exercice.toml").is_file():
        raise BankError(f"exercice inconnu : {exercise_id}")
    where = f"{exercise_id}/exercice.toml"
    data = _read_toml(folder / "exercice.toml")
    allowed = {"titre", "reference", "sorte", "duree_minutes", "timeout_secondes"}
    _check_keys(data, allowed | {"organisation", "fonctions", "contraintes"}, where)
    kind = _text(data, "sorte", where)
    if kind not in KINDS:
        raise BankError(f"{where} : sorte doit valoir {' ou '.join(KINDS)}")
    files, main = _read_layout(data.get("organisation", {}), where)
    functions = tuple(_read_function(item, files, where) for item in data.get("fonctions", []))
    if kind == "programme" and main is None:
        raise BankError(f"{where} : un programme a besoin de organisation.main")
    visible = _read_toml(folder / "tests_visibles.toml")
    private = paths.private / exercise_id
    hidden = _read_toml(private / "tests_caches.toml")
    hints = _read_toml(private / "indices.toml")
    _check_keys(hints, {"indices"}, f"{exercise_id}/indices.toml")
    return Exercise(
        id=exercise_id,
        title=_text(data, "titre", where),
        reference=_text(data, "reference", where),
        kind=kind,
        minutes=int(data.get("duree_minutes", DEFAULT_MINUTES)),
        timeout=float(data.get("timeout_secondes", DEFAULT_TIMEOUT)),
        files=files,
        main=main,
        functions=functions,
        constraints=_read_constraints(data.get("contraintes", {}), functions, where),
        statement=_read_text(folder / "enonce.md"),
        visible_cases=_read_visible(visible, functions, main, f"{exercise_id}/tests_visibles.toml"),
        hidden_cases=_read_hidden(hidden, functions, main, f"{exercise_id}/tests_caches.toml"),
        hints=_strings(hints, "indices", f"{exercise_id}/indices.toml"),
        reference_folder=private / "solution",
    )


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise BankError(f"fichier manquant : {path.parent.name}/{path.name}") from None


def _read_toml(path: Path) -> dict:
    try:
        return tomllib.loads(_read_text(path))
    except tomllib.TOMLDecodeError as error:
        raise BankError(f"{path.parent.name}/{path.name} : {error}") from error


def _check_keys(data: dict, allowed: set[str], where: str) -> None:
    unknown = set(data) - allowed
    if unknown:
        raise BankError(f"{where} : clé inconnue ({', '.join(sorted(unknown))})")


def _text(data: dict, key: str, where: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise BankError(f"{where} : il manque « {key} »")
    return value


def _strings(data: dict, key: str, where: str) -> tuple[str, ...]:
    value = data.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise BankError(f"{where} : « {key} » doit être une liste de textes")
    return tuple(value)


def _read_layout(data: dict, where: str) -> tuple[tuple[str, ...], str | None]:
    _check_keys(data, {"fichiers", "main"}, where)
    files = _strings(data, "fichiers", where)
    if not files:
        raise BankError(f"{where} : organisation.fichiers est vide")
    for name in files:
        path = PurePosixPath(name)
        if "\\" in name or path.is_absolute() or ".." in path.parts:
            raise BankError(f"{where} : chemin invalide ({name})")
        if path.suffix == ".py" and path.parts[0].removesuffix(".py") in sys.stdlib_module_names:
            raise BankError(f"{where} : {name} masque un module de la bibliothèque standard")
    main = data.get("main")
    if main is not None and main not in files:
        raise BankError(f"{where} : {main} n'est pas dans organisation.fichiers")
    return files, main


def _read_function(data: dict, files: tuple[str, ...], where: str) -> FunctionSpec:
    _check_keys(data, {"module", "signature", "preserve_arguments"}, where)
    module, signature = _text(data, "module", where), _text(data, "signature", where)
    try:
        node = ast.parse(f"def {signature}: pass").body[0]
    except SyntaxError as error:
        raise BankError(f"{where} : signature illisible ({signature})") from error
    spec = FunctionSpec(module, node.name, signature, node, data.get("preserve_arguments", False))
    if spec.file not in files:
        raise BankError(f"{where} : {spec.file} n'est pas dans organisation.fichiers")
    return spec


def _read_constraints(
    data: dict, functions: tuple[FunctionSpec, ...], where: str
) -> tuple[ConstraintSet, ...]:
    per_function = data.get("fonctions", {})
    general = {key: value for key, value in data.items() if key != "fonctions"}
    result = [_read_constraint_set(general, None, where)]
    names = {function.name for function in functions}
    for name, content in per_function.items():
        if name not in names:
            raise BankError(f"{where} : contrainte sur une fonction inconnue ({name})")
        result.append(_read_constraint_set(content, name, where))
    return tuple(result)


def _read_constraint_set(data: dict, function: str | None, where: str) -> ConstraintSet:
    keys = {
        "interdits": "forbidden",
        "imposes": "required",
        "fonctions_interdites": "forbidden_functions",
        "modules_interdits": "forbidden_modules",
        "appels_imposes": "required_calls",
    }
    _check_keys(data, set(keys), where)
    for key in ("interdits", "imposes"):
        unknown = set(_strings(data, key, where)) - set(CONSTRUCTS)
        if unknown:
            raise BankError(f"{where} : construction inconnue ({', '.join(sorted(unknown))})")
    values = {attribute: _strings(data, key, where) for key, attribute in keys.items()}
    return ConstraintSet(function=function, **values)


def _read_visible(
    data: dict, functions: tuple[FunctionSpec, ...], main: str | None, where: str
) -> tuple[Case, ...]:
    _check_keys(data, {"tests"}, where)
    cases = []
    for test in data.get("tests", []):
        _check_keys(test, {"appel", "attendu", "entree", "sortie"}, where)
        if "attendu" not in test and "sortie" not in test:
            raise BankError(f"{where} : un test a besoin de « attendu » ou de « sortie »")
        if "appel" not in test and "attendu" in test:
            raise BankError(f"{where} : « attendu » a besoin de « appel »")
        cases.append(
            _build_case(
                functions,
                main,
                where,
                call=test.get("appel"),
                stdin=_strings(test, "entree", where),
                expected=test.get("attendu"),
                output=test.get("sortie"),
            )
        )
    if not cases:
        raise BankError(f"{where} : aucun test")
    return tuple(cases)


def _read_hidden(
    data: dict, functions: tuple[FunctionSpec, ...], main: str | None, where: str
) -> tuple[Case, ...]:
    _check_keys(data, {"groupes"}, where)
    cases = []
    for group in data.get("groupes", []):
        _check_keys(group, {"theme", "appels", "entrees"}, where)
        theme = _text(group, "theme", where)
        for call in _strings(group, "appels", where):
            cases.append(_build_case(functions, main, where, call=call, theme=theme))
        for stdin in group.get("entrees", []):
            lines = _strings({"entrees": stdin}, "entrees", where)
            cases.append(_build_case(functions, main, where, stdin=lines, theme=theme))
    return tuple(cases)


def _build_case(
    functions: tuple[FunctionSpec, ...],
    main: str | None,
    where: str,
    *,
    call: str | None = None,
    stdin: tuple[str, ...] = (),
    expected: str | None = None,
    output: str | None = None,
    theme: str | None = None,
) -> Case:
    try:
        parsed = parse_call(call) if call is not None else None
        value = parse_literal(expected) if expected is not None else None
        function = _find_function(parsed, functions) if parsed else None
    except LiteralError as error:
        # A hidden test must not be revealed, even by an error message.
        raise BankError(f"{where} : {'test illisible' if theme else error}") from error
    if parsed is None and main is None:
        raise BankError(f"{where} : un test sans « appel » a besoin de organisation.main")
    return Case(
        label=parsed.source if parsed else main,
        function=function,
        args=parsed.args if parsed else (),
        kwargs=tuple(parsed.kwargs.items()) if parsed else (),
        stdin=stdin,
        has_value=expected is not None,
        value=value,
        output=output,
        theme=theme,
    )


def _find_function(call: Call, functions: tuple[FunctionSpec, ...]) -> FunctionSpec:
    matches = [
        function
        for function in functions
        if function.name == call.function and call.module in (None, function.module)
    ]
    if len(matches) != 1:
        problem = "inconnue" if not matches else "ambiguë (précise le module)"
        raise LiteralError(f"fonction {problem} dans « {call.source} »")
    return matches[0]
