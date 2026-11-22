"""Calls to ruff and French wording of its messages."""

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

TARGET_VERSION = "py314"
LINE_LENGTH = 120

# What PyCharm shows as an error: undefined names and misplaced statements.
BLOCKING_RULES = ("F70", "F82", "F831", "F62")
QUALITY_RULES = ("E", "W", "N", "A", "F", "PLW1514")
# E226 and E24 are off by default in pycodestyle; the others duplicate our own checks.
IGNORED_RULES = ("E226", "E241", "E242", "E741", "E9", "A005", *BLOCKING_RULES)


class RuffError(RuntimeError):
    """Ruff could not be run."""


@dataclass(frozen=True)
class LintMessage:
    """One message of ruff, in French."""

    file: str
    line: int
    code: str | None
    message: str

    @property
    def is_syntax(self) -> bool:
        """Tell whether ruff could not parse the file."""
        return self.code is None


def lint(folder: Path, files: list[str], select: tuple[str, ...], ignore=()) -> list[LintMessage]:
    """Run ruff on some files.

    The preview mode is needed: without it ruff skips most spacing rules (E2, E3).

    :param folder: the folder holding the files
    :param files: paths relative to the folder
    :param select: rule prefixes to enable
    :param ignore: rule prefixes to disable
    :return: the messages, sorted by file and line
    """
    if not files:
        return []
    command = [
        sys.executable, "-m", "ruff", "check", "--isolated", "--no-cache", "--preview",
        "--ignore-noqa", "--output-format", "json", "--target-version", TARGET_VERSION,
        "--config", f"line-length={LINE_LENGTH}", "--select", ",".join(select),
    ]  # fmt: skip
    if ignore:
        command += ["--ignore", ",".join(ignore)]
    result = subprocess.run(
        [*command, "--", *files], cwd=folder, capture_output=True, encoding="utf-8", check=False
    )
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        detail = result.stderr.strip() or "aucune sortie"
        raise RuffError(f"ruff n'a pas pu s'exécuter : {detail}") from None
    root = folder.resolve()
    messages = [_convert(item, root) for item in data]
    return sorted(messages, key=lambda message: (message.file, message.line, message.code or ""))


def _convert(item: dict, root: Path) -> LintMessage:
    path = Path(item["filename"])
    name = path.relative_to(root).as_posix() if path.is_relative_to(root) else path.name
    code = item["code"]
    line = item["location"]["row"]
    return LintMessage(name, line, code, translate(code, item["message"]))


def translate(code: str | None, message: str) -> str:
    """Word a message of ruff in French.

    :param code: the rule, for example ``"E302"``
    :param message: the original message
    :return: the French message, or the original one for a rare rule
    """
    template = _FRENCH.get(code or "")
    if template is None:
        return message
    quoted = [a or b for a, b in re.findall(r"`([^`]*)`|'([^']*)'", message)]
    numbers = re.findall(r"\d+", message)
    return template.format(
        name=quoted[0] if quoted else "",
        other=quoted[1] if len(quoted) > 1 else "",
        number=numbers[0] if numbers else "",
        last=numbers[-1] if numbers else "",
    )


_FRENCH = {
    "E101": "indentation : tabulations et espaces mélangés",
    "E111": "indentation : un multiple de 4 espaces est attendu",
    "E114": "indentation du commentaire : un multiple de 4 espaces est attendu",
    "E117": "indentation trop grande",
    "E201": "espace en trop après « {name} »",
    "E202": "espace en trop avant « {name} »",
    "E203": "espace en trop avant « {name} »",
    "E211": "espace en trop avant « {name} »",
    "E221": "plusieurs espaces avant un opérateur",
    "E222": "plusieurs espaces après un opérateur",
    "E225": "espace manquant autour d'un opérateur",
    "E227": "espace manquant autour d'un opérateur",
    "E228": "espace manquant autour de %",
    "E231": "espace manquant après « {name} »",
    "E251": "pas d'espace autour du = d'un argument nommé",
    "E252": "espaces attendus autour du = d'un paramètre annoté",
    "E261": "deux espaces attendus avant un commentaire en fin de ligne",
    "E262": "un commentaire commence par « # » suivi d'une espace",
    "E265": "un commentaire commence par « # » suivi d'une espace",
    "E266": "trop de # au début du commentaire",
    "E271": "plusieurs espaces après un mot-clé",
    "E272": "plusieurs espaces avant un mot-clé",
    "E275": "espace manquante après un mot-clé",
    "E301": "une ligne vide attendue avant une méthode",
    "E302": "2 lignes vides attendues avant une fonction (trouvé : {last})",
    "E303": "trop de lignes vides (trouvé : {last})",
    "E304": "pas de ligne vide après un décorateur",
    "E305": "2 lignes vides attendues après une fonction (trouvé : {last})",
    "E306": "une ligne vide attendue avant une fonction imbriquée",
    "E401": "un seul import par ligne",
    "E402": "les imports se placent en haut du fichier",
    "E501": "ligne trop longue ({number} caractères, 120 au maximum)",
    "E502": "\\ inutile entre parenthèses",
    "E701": "plusieurs instructions sur une ligne (après « : »)",
    "E702": "plusieurs instructions sur une ligne (« ; »)",
    "E703": "« ; » inutile en fin de ligne",
    "E711": "compare à None avec « is » ou « is not »",
    "E712": "pas de comparaison à True ou False : teste directement la valeur",
    "E713": "écris « not in »",
    "E714": "écris « is not »",
    "E721": "compare des types avec « is » ou isinstance()",
    "E722": "« except: » sans type d'exception",
    "E731": "définis une fonction avec def plutôt que lambda",
    "E742": "nom de classe ambigu ({name})",
    "E743": "nom de fonction ambigu ({name})",
    "W191": "indentation avec des tabulations",
    "W291": "espaces en fin de ligne",
    "W292": "il manque un retour à la ligne à la fin du fichier",
    "W293": "espaces sur une ligne vide",
    "W391": "lignes vides en trop à la fin du fichier",
    "W605": "séquence d'échappement invalide ({name})",
    "N801": "nom de classe « {name} » : écris EnMajusculesAccolées",
    "N802": "nom de fonction « {name} » : écris en_minuscules",
    "N803": "nom de paramètre « {name} » : écris en_minuscules",
    "N806": "nom de variable « {name} » : écris en_minuscules",
    "N807": "nom de fonction « {name} » : pas de __double souligné__",
    "N815": "nom d'attribut « {name} » : écris en_minuscules",
    "N816": "nom de variable « {name} » : écris en_minuscules (ou EN_MAJUSCULES si constante)",
    "N999": "nom de module « {name} » : écris en_minuscules",
    "A001": "le nom « {name} » écrase une fonction prédéfinie de Python",
    "A002": "le paramètre « {name} » porte le nom d'une fonction prédéfinie de Python",
    "A004": "l'import « {name} » écrase une fonction prédéfinie de Python",
    "PLW1514": "open() sans encodage : ajoute encoding='utf-8'",
    "F401": "import inutilisé ({name})",
    "F403": "« import * » : importe seulement les noms utiles",
    "F405": "« {name} » vient peut-être d'un import * : importe-le explicitement",
    "F541": "f-string sans valeur à insérer",
    "F601": "clé en double dans le dictionnaire",
    "F632": "compare des valeurs avec ==, pas avec is",
    "F811": "« {name} » est défini deux fois",
    "F841": "variable « {name} » jamais utilisée",
    "F821": "nom « {name} » non défini",
    "F822": "nom « {name} » non défini dans __all__",
    "F823": "variable « {name} » utilisée avant d'avoir reçu une valeur",
    "F701": "break en dehors d'une boucle",
    "F702": "continue en dehors d'une boucle",
    "F704": "yield ou await en dehors d'une fonction",
    "F706": "return en dehors d'une fonction",
    "F707": "un « except: » sans type doit être le dernier",
    "F831": "paramètre en double dans la fonction ({name})",
}
