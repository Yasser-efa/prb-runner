"""Step 3 of the verdict, first half: running code in an isolated process."""

import ast
import pickle
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from prb.literals import LiteralError, parse_literal
from prb.model import Case
from prb.sources import IGNORED_FOLDERS

HARNESS = Path(__file__).with_name("harness.py")
MAX_TIMEOUTS = 2
STARTUP_MARGIN = 10.0
_FRAME = re.compile(r'File "(?P<file>.+?)", line (?P<line>\d+) in (?P<function>.+)')


@dataclass(frozen=True)
class RunError:
    """An exception, located in the student's files."""

    type: str
    message: str
    file: str | None = None
    line: int | None = None
    source: str | None = None
    function: str | None = None


@dataclass(frozen=True)
class Outcome:
    """What happened when a case was run.

    ``status`` is one of: value, exception, timeout, flood, crash, skipped, absent.
    """

    status: str
    value: object = None
    plain: bool = False
    shown: str = ""
    type_name: str = ""
    output: str = ""
    error: RunError | None = None
    modified: tuple[int | str, ...] = ()
    during_import: bool = False
    truth: bool | None = None


@dataclass
class RunReport:
    """Outcomes of all the cases, and modules that display something when imported."""

    outcomes: list[Outcome]
    noisy_modules: list[str] = field(default_factory=list)


def run_cases(
    folder: Path,
    cases: Sequence[Case],
    main: str | None = None,
    timeout: float = 2.0,
    extra_files: Mapping[str, bytes] | None = None,
) -> RunReport:
    """Run some cases on a copy of a folder.

    Function calls share one process, as in a real program. The whole program is run in a
    new process each time.

    :param folder: the folder holding the code
    :param cases: the calls and programs to run
    :param main: path of the main program, relative to the folder
    :param timeout: maximum duration of one case, in seconds
    :param extra_files: files added to the copy
    :return: one outcome per case, in the same order
    """
    with tempfile.TemporaryDirectory(prefix="prb_", ignore_cleanup_errors=True) as name:
        workspace = Path(name).resolve()
        project = workspace / "projet"
        if folder.is_dir():
            shutil.copytree(folder, project, ignore=shutil.ignore_patterns(*IGNORED_FOLDERS))
        else:
            project.mkdir()
        for file, content in (extra_files or {}).items():
            target = project / file
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        session = _Session(workspace, project, main, timeout)
        calls = [index for index, case in enumerate(cases) if not case.is_program]
        session.run(cases, calls)
        for index, case in enumerate(cases):
            if case.is_program:
                session.run(cases, [index])
        outcomes = [session.outcomes[index] for index in range(len(cases))]
        return RunReport(outcomes, sorted(session.noisy_modules))


class _Session:
    """Launches the harness as often as needed and collects its results."""

    def __init__(self, workspace: Path, project: Path, main: str | None, timeout: float) -> None:
        self.workspace = workspace
        self.project = project
        self.main = main
        self.timeout = timeout
        self.outcomes: dict[int, Outcome] = {}
        self.noisy_modules: set[str] = set()
        self.timeouts: Counter[str] = Counter()

    def run(self, cases: Sequence[Case], indexes: list[int]) -> None:
        pending = list(indexes)
        while pending := self._without_slow_functions(cases, pending):
            events, problem = self._launch(cases, pending)
            current, loading = self._read_events(events)
            if current is not None:
                stopped = self._stopped(problem)
                self.outcomes[current] = stopped
                if stopped.status == "timeout":
                    self.timeouts[cases[current].target] += 1
                if loading:
                    self._spread(cases, pending, loading, stopped)
            elif problem is not None:
                stopped = Outcome("crash", error=RunError("Arrêt", problem))
                self.outcomes.update(
                    (index, stopped) for index in pending if index not in self.outcomes
                )
            pending = [index for index in pending if index not in self.outcomes]

    def _without_slow_functions(self, cases: Sequence[Case], pending: list[int]) -> list[int]:
        """Skip the remaining cases of a function that ran out of time repeatedly."""
        kept = []
        for index in pending:
            if self.timeouts[cases[index].target] >= MAX_TIMEOUTS:
                self.outcomes[index] = Outcome("skipped")
            else:
                kept.append(index)
        return kept

    def _launch(self, cases: Sequence[Case], indexes: list[int]) -> tuple[list[dict], str | None]:
        """Run the harness once.

        :return: the events it reported and, if it did not finish, why
        """
        job, results, trace = (self.workspace / name for name in ("job", "results", "trace"))
        job.write_bytes(pickle.dumps(self._job(cases, indexes)))
        for file in (results, trace):
            file.write_text("", encoding="utf-8")
        command = [sys.executable, "-I", "-X", "utf8", "-B", str(HARNESS)]
        limit = STARTUP_MARGIN + (len(indexes) + 1) * self.timeout
        problem = None
        try:
            process = subprocess.run(
                [*command, str(job), str(results), str(trace)],
                cwd=self.project,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                timeout=limit,
                check=False,
            )
            if process.returncode != 0:
                lines = process.stderr.decode("utf-8", "replace").strip().splitlines()
                problem = lines[-1] if lines else f"code de sortie {process.returncode}"
        except subprocess.TimeoutExpired:
            problem = "timeout"
        text = results.read_text(encoding="utf-8")
        return [ast.literal_eval(line) for line in text.split("\n")[:-1]], problem

    def _job(self, cases: Sequence[Case], indexes: list[int]) -> dict:
        return {
            "project": str(self.project),
            "main": self.main,
            "timeout": self.timeout,
            "cases": [_describe_case(index, cases[index]) for index in indexes],
        }

    def _read_events(self, events: list[dict]) -> tuple[int | None, str | None]:
        """Store the results.

        :return: the case and the module import that were interrupted, if any
        """
        current = loading = None
        for event in events:
            match event["event"]:
                case "start":
                    current = event["index"]
                case "import":
                    loading = event["module"]
                case "import_output":
                    self.noisy_modules.add(event["module"])
                case "imported":
                    loading = None
                case "result":
                    self.outcomes[event["index"]] = _read_outcome(event)
                    current = None
        return current, loading

    def _stopped(self, problem: str | None) -> Outcome:
        """Describe the case during which the harness stopped."""
        frame = self._read_trace()
        if frame or problem == "timeout":
            return Outcome("timeout", error=frame or RunError("Timeout", ""))
        return Outcome("crash", error=RunError("Arrêt", problem or "arrêt brutal de Python"))

    def _read_trace(self) -> RunError | None:
        """Find the student's line that was running when time ran out."""
        text = (self.workspace / "trace").read_text(encoding="utf-8", errors="replace")
        if "Timeout" not in text:
            return None
        marker = f"{self.workspace.name}\\projet\\".replace("\\", "/")
        for match in _FRAME.finditer(text):
            path = match["file"].replace("\\", "/")
            if marker in path:
                name, line = path.split(marker, 1)[1], int(match["line"])
                return RunError(
                    "Timeout", "", name, line, self._source_line(name, line), match["function"]
                )
        return RunError("Timeout", "")

    def _source_line(self, name: str, line: int) -> str | None:
        try:
            lines = (self.project / name).read_text(encoding="utf-8").splitlines()
            return lines[line - 1].strip()
        except (OSError, UnicodeDecodeError, IndexError):
            return None

    def _spread(
        self, cases: Sequence[Case], pending: list[int], module: str, stopped: Outcome
    ) -> None:
        """Give the same outcome to every case of a module that cannot be imported."""
        for index in pending:
            function = cases[index].function
            if function and function.module == module:
                self.outcomes[index] = stopped


def _describe_case(index: int, case: Case) -> dict:
    """Describe a case with plain values, for the harness."""
    function, after = case.function, None
    if case.after is not None:
        if case.after in dict(case.kwargs):
            after = ("kwargs", case.after)
        else:
            after = ("args", function.parameters.index(case.after))
    return {
        "index": index,
        "module": function.module if function else None,
        "function": function.name if function else None,
        "preserve": bool(function and function.preserve_arguments),
        "args": case.args,
        "kwargs": dict(case.kwargs),
        "stdin": case.stdin,
        "after": after,
        "seed": case.seed,
    }


def _read_outcome(event: dict) -> Outcome:
    error = RunError(**event["error"]) if "error" in event else None
    value, plain = None, False
    if event.get("value") is not None:
        try:
            value, plain = parse_literal(event["value"]), True
        except LiteralError:
            plain = False
    return Outcome(
        status=event["status"],
        value=value,
        plain=plain,
        shown=event.get("shown", ""),
        type_name=event.get("type", ""),
        output=event["output"],
        error=error,
        modified=tuple(event.get("modified", ())),
        during_import=event.get("during_import", False),
        truth=event.get("truth"),
    )
