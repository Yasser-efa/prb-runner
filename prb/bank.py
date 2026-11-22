"""Reading of the exercise bank (TOML and Markdown files)."""

import ast
import difflib
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from prb.case_reader import CaseReader
from prb.constructs import CONSTRUCTS
from prb.controls import load_controls
from prb.model import BankError, ConstraintSet, Exercise, FunctionSpec, ProvidedFile
from prb.paths import Paths
from prb.sources import list_files

DEFAULT_MINUTES = 40
DEFAULT_TIMEOUT = 2.0
MAX_SUGGESTIONS = 6
KINDS = ("fonction", "programme")
_ID_PATTERN = re.compile(r"[a-z][a-z0-9_]*")


@dataclass(frozen=True)
class _Layout:
    """Files of an exercise."""

    files: tuple[str, ...]
    main: str | None
    provided: tuple[ProvidedFile, ...]


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
        raise BankError(f"exercice inconnu : {exercise_id}{_suggest(paths, exercise_id)}")
    where = f"{exercise_id}/exercice.toml"
    data = _read_toml(folder / "exercice.toml")
    allowed = {"titre", "reference", "sorte", "duree_minutes", "timeout_secondes"}
    _check_keys(data, allowed | {"organisation", "fonctions", "contraintes"}, where)
    kind = _text(data, "sorte", where)
    if kind not in KINDS:
        raise BankError(f"{where} : sorte doit valoir {' ou '.join(KINDS)}")
    layout = _read_layout(data.get("organisation", {}), paths.root, where)
    if kind == "programme" and layout.main is None:
        raise BankError(f"{where} : un programme a besoin de organisation.main")
    functions = tuple(
        _read_function(item, layout.files, where) for item in data.get("fonctions", [])
    )
    private = paths.private / exercise_id
    controls = load_controls(private / "controles.py")

    def reader(name: str) -> CaseReader:
        return CaseReader(f"{exercise_id}/{name}", functions, layout.main, controls)

    hints = _read_toml(private / "indices.toml")
    _check_keys(hints, {"indices"}, f"{exercise_id}/indices.toml")
    visible, hidden = "tests_visibles.toml", "tests_caches.toml"
    return Exercise(
        id=exercise_id,
        title=_text(data, "titre", where),
        reference=_text(data, "reference", where),
        kind=kind,
        minutes=int(data.get("duree_minutes", DEFAULT_MINUTES)),
        timeout=float(data.get("timeout_secondes", DEFAULT_TIMEOUT)),
        files=layout.files,
        main=layout.main,
        provided=layout.provided,
        functions=functions,
        constraints=_read_constraints(data.get("contraintes", {}), functions, where),
        statement=_read_text(folder / "enonce.md"),
        visible_cases=reader(visible).read_visible(_read_toml(folder / visible)),
        hidden_cases=reader(hidden).read_hidden(_read_toml(private / hidden)),
        hidden_files=tuple(
            (name, private / "fichiers" / name) for name in list_files(private / "fichiers")
        ),
        hints=_strings(hints, "indices", f"{exercise_id}/indices.toml"),
        reference_folder=private / "solution",
    )


def _suggest(paths: Paths, text: str) -> str:
    """Look for the exercises that the student may have meant."""
    names = sorted(path.parent.name for path in paths.exercises.glob("*/exercice.toml"))
    found = [name for name in names if text and text.casefold() in name]
    found = found or difflib.get_close_matches(text, names)
    return f" (peut-être : {', '.join(found[:MAX_SUGGESTIONS])})" if found else ""


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


def _read_layout(data: dict, root: Path, where: str) -> _Layout:
    _check_keys(data, {"fichiers", "main", "fournis", "modifiables"}, where)
    files = _strings(data, "fichiers", where)
    if not files:
        raise BankError(f"{where} : organisation.fichiers est vide")
    sources = data.get("fournis", {})
    editable = _strings(data, "modifiables", where)
    for name in (*files, *sources, *sources.values()):
        path = PurePosixPath(name)
        if "\\" in name or path.is_absolute() or ".." in path.parts:
            raise BankError(f"{where} : chemin invalide ({name})")
    for name in (*files, *sources):
        path = PurePosixPath(name)
        if path.suffix == ".py" and path.parts[0].removesuffix(".py") in sys.stdlib_module_names:
            raise BankError(f"{where} : {name} masque un module de la bibliothèque standard")
    if set(files) & set(sources):
        raise BankError(f"{where} : un fichier ne peut pas être à la fois demandé et fourni")
    if set(editable) - set(sources):
        raise BankError(f"{where} : organisation.modifiables contient un fichier non fourni")
    main = data.get("main")
    if main is not None and main not in files:
        raise BankError(f"{where} : {main} n'est pas dans organisation.fichiers")
    provided = tuple(_read_provided(name, sources[name], root, editable) for name in sources)
    return _Layout(files, main, provided)


def _read_provided(name: str, source: str, root: Path, editable: tuple[str, ...]) -> ProvidedFile:
    """Locate a provided file, written « file » or « archive.zip::member »."""
    path, _, member = source.partition("::")
    return ProvidedFile(name, root / path, member or None, name in editable)


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
        "modules_imposes": "required_modules",
        "appels_imposes": "required_calls",
    }
    _check_keys(data, set(keys), where)
    for key in ("interdits", "imposes"):
        unknown = set(_strings(data, key, where)) - set(CONSTRUCTS)
        if unknown:
            raise BankError(f"{where} : construction inconnue ({', '.join(sorted(unknown))})")
    values = {attribute: _strings(data, key, where) for key, attribute in keys.items()}
    return ConstraintSet(function=function, **values)
