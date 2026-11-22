"""Controls of the « Qui est-ce ? » exam, whose results are random."""

import re

_ATTRIBUTES = (
    "lunettes", "chapeau", "yeux clairs", "cheveux foncés", "pilosité faciale", "écharpe",
)  # fmt: skip
_CHARACTERS, _QUESTIONS = 36, 6
_WELCOME = [
    "Bienvenue dans Qui-est-ce ? Essayez de deviner le personnage que j'ai choisi !",
    "Voici les caractéristiques possibles :",
    ", ".join(_ATTRIBUTES),
]
_PROMPT = "Posez une question (exemple : lunettes = oui) :"
_VALID = re.compile(rf"\s*({'|'.join(_ATTRIBUTES)})\s*=\s*(oui|non)\s*")


def resume_lignes(outcome, case):
    """Summarise a long list of lines."""
    lines = outcome.value
    return len(lines), lines[0], lines[1], lines[-1]


def sans_prenoms(outcome, case):
    """Check the random names, then remove them."""
    names = [character["prenom"] for character in outcome.value]
    if len(set(names)) != len(names):
        return "des personnages ont le même prénom"
    if not set(names) <= set(case.args[0]):
        return "un prénom ne vient pas de la liste"
    return [
        {key: value for key, value in character.items() if key != "prenom"}
        for character in outcome.value
    ]


def _read_character(line):
    name, _, rest = line.rstrip(".,").partition(" : ")
    attributes = frozenset(part.strip() for part in rest.split(",") if part.strip())
    return name.strip(), attributes


def _read_lists(lines):
    """Read every « Il reste N personnage(s) » and the characters below it."""
    lists = []
    for rank, line in enumerate(lines):
        found = re.fullmatch(r"Il reste (\d+) personnage\(s\) :", line)
        if found:
            count = int(found[1])
            lists.append([_read_character(text) for text in lines[rank + 1 : rank + 1 + count]])
    return lists


def _check_first(lines, first):
    if lines[:3] != _WELCOME:
        return "les trois premières lignes ne sont pas celles qui sont demandées"
    if len(first) != _CHARACTERS:
        return f"la partie doit commencer avec {_CHARACTERS} personnages"
    if len({name for name, _ in first}) != _CHARACTERS:
        return "des personnages ont le même prénom"
    if len({attributes for _, attributes in first}) != _CHARACTERS:
        return "des personnages ont les mêmes attributs"
    if not all(attributes <= set(_ATTRIBUTES) for _, attributes in first):
        return "un attribut affiché n'existe pas"
    return None


def _splits(characters, attribute):
    """The two possible results of a question."""
    return [
        [item for item in characters if (attribute in item[1]) is wanted]
        for wanted in (True, False)
    ]


def partie_coherente(outcome, case):
    """Check that a game follows the rules, whatever the random choices."""
    lines = [line.strip() for line in outcome.output.splitlines() if line.strip()]
    matches = [_VALID.fullmatch(line.lower()) for line in case.stdin]
    questions = [match[1] for match in matches if match]
    lists = _read_lists(lines)
    if not lists:
        return "aucune liste de personnages n'est affichée"
    problem = _check_first(lines, lists[0])
    if problem:
        return problem
    for before, after, attribute in zip(lists, lists[1:], questions):
        if after not in _splits(before, attribute):
            return f"après la question sur « {attribute} », la liste est incorrecte"
    if any(len(characters) < 2 for characters in lists):
        return "la partie continue alors qu'il ne reste qu'un personnage"
    if not any(line.startswith(_PROMPT) for line in lines):
        return "l'invite n'est pas celle qui est demandée"
    asked = questions[len(lists) - 1 : len(lists)]
    invalid = sum(match is None for match in matches)
    if lines.count("Format invalide. Utilisez 'attribut=valeur'.") != invalid:
        return "« Format invalide. » n'est pas affiché comme demandé"
    last = re.fullmatch(r"(Bravo ! Le personnage est|Perdu ! Le personnage était) (.+)\.", lines[-1])
    if not last or not asked:
        return "la dernière ligne n'est pas celle qui est demandée"
    results = [split for split in _splits(lists[-1], asked[0]) if last[2] in dict(split)]
    if not results:
        return "le personnage annoncé n'est pas possible"
    if last[1].startswith("Bravo"):
        return "partie gagnée et cohérente" if len(results[0]) == 1 else "victoire annoncée trop tôt"
    if len(lists) != _QUESTIONS:
        return f"la partie doit durer {_QUESTIONS} questions"
    return "partie perdue et cohérente" if len(results[0]) > 1 else "défaite annoncée à tort"
