"""Reading of the visible and hidden tests."""

from collections.abc import Callable
from dataclasses import dataclass, replace
from types import SimpleNamespace

from prb.literals import Call, LiteralError, parse_call, parse_literal
from prb.model import BankError, Case, FunctionSpec

_SHARED_KEYS = {"apres", "controle", "graine"}


@dataclass(frozen=True)
class CaseReader:
    """Turns the tables of a test file into cases."""

    where: str
    functions: tuple[FunctionSpec, ...]
    main: str | None
    controls: dict[str, Callable]

    def read_visible(self, data: dict) -> tuple[Case, ...]:
        """Read ``tests_visibles.toml``.

        :param data: the content of the file
        :return: the cases, in order
        """
        self._check_keys(data, {"tests"})
        keys = {"appel", "attendu", "entree", "sortie", "libelle"} | _SHARED_KEYS
        cases = []
        for test in data.get("tests", []):
            self._check_keys(test, keys)
            if "attendu" not in test and "sortie" not in test:
                raise self._error("un test a besoin de « attendu » ou de « sortie »")
            if "appel" not in test and "attendu" in test and "controle" not in test:
                raise self._error("« attendu » a besoin de « appel » ou de « controle »")
            cases.append(self._build(test))
        if not cases:
            raise self._error("aucun test")
        return tuple(cases)

    def read_hidden(self, data: dict) -> tuple[Case, ...]:
        """Read ``tests_caches.toml``.

        :param data: the content of the file
        :return: the cases, in order
        """
        self._check_keys(data, {"groupes"})
        keys = {"theme", "appels", "entrees", "tests", "ignorer_sortie"} | _SHARED_KEYS
        cases = []
        for group in data.get("groupes", []):
            self._check_keys(group, keys)
            theme = group.get("theme")
            if not isinstance(theme, str) or not theme:
                raise self._error("il manque « theme »")
            shared = {key: group[key] for key in _SHARED_KEYS if key in group}
            tests = [{"appel": call} for call in self._strings(group, "appels")]
            tests += [{"entree": lines} for lines in group.get("entrees", [])]
            for test in group.get("tests", []):
                self._check_keys(test, {"appel", "entree", "graine"})
                tests.append(test)
            compare_output = not group.get("ignorer_sortie", False)
            for test in tests:
                cases.append(self._build(shared | test, theme, compare_output))
        return tuple(cases)

    def _build(self, test: dict, theme: str | None = None, compare_output: bool = True) -> Case:
        expected = test.get("attendu")
        try:
            call = parse_call(test["appel"]) if "appel" in test else None
            value = parse_literal(expected) if expected is not None else None
            function = self._find_function(call) if call else None
        except LiteralError as error:
            # A hidden test must not be revealed, even by an error message.
            raise self._error("test illisible" if theme else str(error)) from error
        if call is None and self.main is None:
            raise self._error("un test sans « appel » a besoin de organisation.main")
        after = test.get("apres")
        if after is not None and (function is None or after not in function.parameters):
            raise self._error(f"« apres » doit être un paramètre ({after})")
        case = Case(
            label=test.get("libelle") or (call.source if call else self.main),
            function=function,
            args=call.args if call else (),
            kwargs=tuple(call.kwargs.items()) if call else (),
            stdin=self._strings(test, "entree"),
            has_value=expected is not None,
            value=value,
            output=test.get("sortie"),
            theme=theme,
            after=after,
            control=self._find_control(test.get("controle")),
            seed=test.get("graine"),
            compare_output=compare_output,
        )
        if case.control is None or case.output is None:
            return case
        # The expected display goes through the control too.
        expected_outcome = SimpleNamespace(value=None, truth=None, output=case.output)
        value = case.control(expected_outcome, case)
        return replace(case, has_value=True, value=value, output=None)

    def _find_function(self, call: Call) -> FunctionSpec:
        matches = [
            function
            for function in self.functions
            if function.name == call.function and call.module in (None, function.module)
        ]
        if len(matches) != 1:
            problem = "inconnue" if not matches else "ambiguë (précise le module)"
            raise LiteralError(f"fonction {problem} dans « {call.source} »")
        return matches[0]

    def _find_control(self, name: str | None) -> Callable | None:
        if name is not None and name not in self.controls:
            raise self._error(f"contrôle inconnu ({name})")
        return self.controls[name] if name else None

    def _strings(self, data: dict, key: str) -> tuple[str, ...]:
        value = data.get(key, [])
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise self._error(f"« {key} » doit être une liste de textes")
        return tuple(value)

    def _check_keys(self, data: dict, allowed: set[str]) -> None:
        unknown = set(data) - allowed
        if unknown:
            raise self._error(f"clé inconnue ({', '.join(sorted(unknown))})")

    def _error(self, message: str) -> BankError:
        return BankError(f"{self.where} : {message}")
