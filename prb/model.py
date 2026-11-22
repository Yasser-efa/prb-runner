"""What an exercise is made of."""

import ast
import zipfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


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

    @property
    def parameters(self) -> list[str]:
        """Names of the parameters that can be given by position."""
        arguments = self.node.args
        return [arg.arg for arg in [*arguments.posonlyargs, *arguments.args]]


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
class ProvidedFile:
    """A file that the student receives with the statement."""

    name: str
    path: Path
    member: str | None = None
    editable: bool = False

    def read(self) -> bytes:
        """Read the original content, possibly inside a ZIP archive.

        :return: the content
        :raises BankError: if the original cannot be found
        """
        try:
            if self.member is None:
                return self.path.read_bytes()
            with zipfile.ZipFile(self.path) as archive:
                return archive.read(self.member)
        except (OSError, KeyError, zipfile.BadZipFile) as error:
            raise BankError(f"fichier fourni introuvable : {self.path} ({error})") from error

    def matches(self, content: bytes) -> bool:
        """Tell whether a copy is intact, whatever its line endings.

        :param content: the content of the copy
        :return: True if the copy was not modified
        """
        return content.replace(b"\r\n", b"\n") == self.read().replace(b"\r\n", b"\n")


@dataclass(frozen=True)
class Case:
    """One execution of the code: a function call, or the whole program.

    ``after`` names a parameter: its value after the call is compared instead of the returned
    value. ``control`` computes what is compared from what happened.
    """

    label: str
    function: FunctionSpec | None = None
    args: tuple = ()
    kwargs: tuple[tuple[str, object], ...] = ()
    stdin: tuple[str, ...] = ()
    has_value: bool = False
    value: object = None
    output: str | None = None
    theme: str | None = None
    after: str | None = None
    control: Callable | None = None
    seed: int | None = None
    compare_output: bool = True

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
    provided: tuple[ProvidedFile, ...]
    functions: tuple[FunctionSpec, ...]
    constraints: tuple[ConstraintSet, ...]
    statement: str
    visible_cases: tuple[Case, ...]
    hidden_cases: tuple[Case, ...]
    hidden_files: tuple[tuple[str, Path], ...]
    hints: tuple[str, ...]
    reference_folder: Path

    @property
    def provided_names(self) -> set[str]:
        """Paths of the provided files."""
        return {file.name for file in self.provided}

    def test_files(self) -> dict[str, bytes]:
        """Read the data files added to the student's folder during the tests only."""
        return {name: path.read_bytes() for name, path in self.hidden_files}
