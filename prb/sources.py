"""Reading of the student's folder and of its Python files."""

import ast
import io
import tokenize
import warnings
from dataclasses import dataclass
from pathlib import Path

IGNORED_FOLDERS = {"__pycache__", ".idea", ".venv", "venv", ".git", ".ruff_cache", ".pytest_cache"}


@dataclass(frozen=True)
class Problem:
    """Something to report about the student's code."""

    message: str
    file: str | None = None
    line: int | None = None
    source: str | None = None
    group: str = ""

    @property
    def location(self) -> str:
        """Readable position, empty when the problem is not tied to a file."""
        if self.file is None:
            return ""
        return f"{self.file}, ligne {self.line}" if self.line else self.file


@dataclass(frozen=True)
class SourceFile:
    """A Python file of the student, parsed when its syntax is correct."""

    name: str
    text: str
    tree: ast.Module | None
    error: Problem | None = None

    @property
    def module(self) -> str:
        """Dotted name used to import the file from the project root."""
        dotted = self.name.removesuffix(".py").replace("/", ".")
        return dotted.removesuffix(".__init__")

    @property
    def is_package(self) -> bool:
        """Tell whether the file is the ``__init__.py`` of a package."""
        return self.name.rsplit("/", 1)[-1] == "__init__.py"

    def line(self, number: int | None) -> str | None:
        """Return the text of a line, without its indentation."""
        lines = self.text.splitlines()
        if number is None or not 1 <= number <= len(lines):
            return None
        return lines[number - 1].strip()


def list_files(folder: Path) -> list[str]:
    """List the files of a folder with their exact names, recursively.

    :param folder: the folder to scan
    :return: relative paths written with ``/``, caches and IDE folders excluded
    """
    if not folder.is_dir():
        return []
    found = []
    for path in sorted(folder.rglob("*")):
        relative = path.relative_to(folder)
        if path.is_file() and not IGNORED_FOLDERS.intersection(relative.parts):
            found.append(relative.as_posix())
    return found


def read_sources(folder: Path) -> dict[str, SourceFile]:
    """Read every Python file of a folder.

    :param folder: the student's folder
    :return: the files, indexed by relative path
    """
    return {
        name: _read_source(folder, name) for name in list_files(folder) if name.endswith(".py")
    }


def _read_source(folder: Path, name: str) -> SourceFile:
    data = (folder / name).read_bytes()
    try:
        encoding, _ = tokenize.detect_encoding(io.BytesIO(data).readline)
        text = data.decode(encoding)
    except (SyntaxError, UnicodeDecodeError, LookupError):
        problem = Problem("le fichier n'est pas encodé en UTF-8", name)
        return SourceFile(name, data.decode("utf-8", "replace"), None, problem)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # compile() also rejects « return » outside a function, unlike ast.parse().
            compile(text, name, "exec", dont_inherit=True)
            tree = ast.parse(text, name)
    except SyntaxError as error:
        source = (error.text or "").strip() or None
        problem = Problem(f"{type(error).__name__} : {error.msg}", name, error.lineno, source)
        return SourceFile(name, text, None, problem)
    except (ValueError, RecursionError, MemoryError) as error:
        return SourceFile(name, text, None, Problem(f"fichier illisible : {error}", name))
    return SourceFile(name, text, tree)
