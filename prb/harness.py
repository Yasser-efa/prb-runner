"""Runs the student's code. This file is executed in a separate, isolated process.

Usage: python -I -X utf8 -B harness.py JOB RESULTS TRACE

JOB is a pickle written by runner.py. Each line written to RESULTS is the repr of a
dictionary, flushed at once so that nothing is lost if the process is killed. TRACE
receives the traceback of the line being executed when a test takes too long.

Only the standard library is available here, and everything needed is imported before
the student's folder is added to the import path.
"""

import builtins
import copy
import faulthandler
import importlib
import io
import os
import pickle
import runpy
import sys
import traceback

MAX_OUTPUT = 200_000
MAX_VALUE = 200_000
MAX_MESSAGE = 500


class OutputLimitError(BaseException):
    """The student's code displays far too much."""


class NotPlainError(Exception):
    """The value cannot be sent back as a plain Python literal."""


class BoundedOutput(io.TextIOBase):
    """Text stream that stops the program when it writes too much."""

    def __init__(self):
        self.parts = []
        self.size = 0

    def writable(self):
        return True

    def write(self, text):
        self.size += len(text)
        if self.size > MAX_OUTPUT:
            raise OutputLimitError
        self.parts.append(text)
        return len(text)

    def getvalue(self):
        return "".join(self.parts)


class Harness:
    """Executes the cases of a job and reports on each of them."""

    def __init__(self, job, results, trace):
        self.project = job["project"]
        self.main = job["main"]
        self.timeout = job["timeout"]
        self.cases = job["cases"]
        self.results = results
        self.trace = trace
        self.modules = {}

    def run(self):
        for case in self.cases:
            self.report(event="start", index=case["index"])
            if case["module"] is None:
                result = self.run_program(case)
            else:
                result = self.run_function(case)
            self.report(event="result", index=case["index"], **result)

    def report(self, **event):
        self.results.write(repr(event) + "\n")
        self.results.flush()

    def run_program(self, case):
        path = os.path.join(self.project, *self.main.split("/"))
        sys.argv = [path]

        def program():
            try:
                runpy.run_path(path, run_name="__main__")
            except SystemExit as stop:
                if stop.code not in (None, 0):
                    raise

        return self.observe(program, case["stdin"])

    def run_function(self, case):
        name = case["module"]
        if name not in self.modules:
            self.report(event="import", module=name)
            holder = {}

            def load():
                holder["module"] = importlib.import_module(name)

            result = self.observe(load, ())
            self.modules[name] = (holder.get("module"), result)
            if result["output"]:
                self.report(event="import_output", module=name)
            self.report(event="imported", module=name)
        module, loading = self.modules[name]
        if module is None:
            return {**loading, "during_import": True}
        args, kwargs = case["args"], case["kwargs"]
        before = copy.deepcopy((args, kwargs)) if case["preserve"] else None

        def call():
            return getattr(module, case["function"])(*args, **kwargs)

        result = self.observe(call, case["stdin"])
        if before is not None:
            result["modified"] = modified_arguments(before, (args, kwargs))
        return result

    def observe(self, action, stdin):
        """Run an action with a fake keyboard and screen, and describe what happens."""
        output = BoundedOutput()
        keyboard = io.StringIO("".join(line + "\n" for line in stdin))
        saved = sys.stdin, sys.stdout, sys.stderr, builtins.input
        sys.stdin, sys.stdout, sys.stderr = keyboard, output, BoundedOutput()
        builtins.input = make_input(keyboard, output)
        result = {"output": ""}
        faulthandler.dump_traceback_later(self.timeout, exit=True, file=self.trace)
        try:
            value = action()
        except OutputLimitError as error:
            result["status"] = "flood"
            result["error"] = describe_error(error, self.project)
        except BaseException as error:
            result["status"] = "exception"
            result["error"] = describe_error(error, self.project)
        else:
            result["status"] = "value"
            result.update(describe_value(value))
        finally:
            faulthandler.cancel_dump_traceback_later()
            sys.stdin, sys.stdout, sys.stderr, builtins.input = saved
        result["output"] = output.getvalue()
        return result


def make_input(keyboard, output):
    """Build an input() that shows the prompt and the typed text, as PyCharm does."""

    def fake_input(prompt="", /):
        output.write(str(prompt))
        line = keyboard.readline()
        if not line:
            raise EOFError("EOF when reading a line")
        output.write(line)
        return line.rstrip("\n")

    return fake_input


def describe_value(value):
    """Turn a returned value into text that the parent process can read back."""
    result = {"type": type(value).__name__, "value": None}
    try:
        text = repr(to_plain(value))
        if len(text) <= MAX_VALUE:
            result["value"] = text
    except (NotPlainError, RecursionError, ValueError):
        pass
    try:
        shown = repr(value)
    except Exception:
        shown = f"<{type(value).__name__}>"
    result["shown"] = shown[:MAX_MESSAGE]
    return result


def to_plain(value):
    """Convert subclasses (Counter, namedtuple…) to the basic type they extend."""
    if value is None or type(value) in (bool, int, float, complex, str, bytes):
        return value
    if isinstance(value, str):
        return str.__str__(value)
    for base in (int, float, bytes):
        if isinstance(value, base):
            return base(value)
    for base in (list, tuple, set, frozenset):
        if isinstance(value, base):
            return base(to_plain(item) for item in value)
    if isinstance(value, dict):
        return {to_plain(key): to_plain(item) for key, item in value.items()}
    raise NotPlainError


def describe_error(error, project):
    """Describe an exception from the point of view of the student's own files."""
    own = [
        frame
        for frame in traceback.extract_tb(error.__traceback__)
        if is_inside(frame.filename, project)
    ]
    try:
        message = str(error)
    except Exception:
        message = ""
    result = {
        "type": type(error).__name__,
        "message": message[:MAX_MESSAGE],
        "file": None,
        "line": None,
        "source": None,
        "function": None,
    }
    if own:
        last = own[-1]
        result.update(line=last.lineno, source=last.line, function=last.name)
        result["file"] = relative(last.filename, project)
    elif isinstance(error, SyntaxError) and error.filename and is_inside(error.filename, project):
        result.update(line=error.lineno, source=(error.text or "").strip())
        result["file"] = relative(error.filename, project)
    return result


def is_inside(filename, project):
    # Names such as "<frozen runpy>" are relative: they must not be resolved from the project.
    if not os.path.isabs(filename):
        return False
    path = os.path.normcase(os.path.abspath(filename))
    return path.startswith(os.path.normcase(project) + os.sep)


def relative(filename, project):
    return os.path.relpath(os.path.abspath(filename), project).replace(os.sep, "/")


def modified_arguments(before, after):
    """List the positions and names of the arguments changed by the call."""
    pairs = enumerate(zip(before[0], after[0], strict=True))
    changed = [index for index, (old, new) in pairs if old != new]
    return changed + [name for name in before[1] if before[1][name] != after[1][name]]


def main():
    job_path, results_path, trace_path = sys.argv[1:4]
    with open(job_path, "rb") as file:
        job = pickle.load(file)
    os.chdir(job["project"])
    sys.path.insert(0, job["project"])
    with (
        open(results_path, "w", encoding="utf-8") as results,
        open(trace_path, "w", encoding="utf-8") as trace,
    ):
        Harness(job, results, trace).run()
        results.flush()


if __name__ == "__main__":
    main()
