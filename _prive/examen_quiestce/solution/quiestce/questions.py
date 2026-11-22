"""Lecture des questions posées par le joueur."""

import re
from collections.abc import Collection

SEPARATEUR = "="


def is_question_valide(question: str, attributs: Collection[str]) -> bool:
    """
    Vérifie si une question est de la forme « attribut = valeur ».

    :param question: la question à vérifier
    :param attributs: les attributs autorisés
    :return: vrai si la question est valide
    """
    motif = rf"({'|'.join(attributs)}) *{SEPARATEUR} *(oui|non)"
    return bool(re.fullmatch(motif, question))


def lire_question_utilisateur(invite: str, attributs: Collection[str]) -> tuple[str, str]:
    """
    Demande une question jusqu'à ce que son format soit correct.

    :param invite: le texte affiché avant la saisie
    :param attributs: les attributs autorisés
    :return: l'attribut et la valeur, en minuscules
    """
    question = input(invite).lower()
    while not is_question_valide(question, attributs):
        print("Format invalide. Utilisez 'attribut=valeur'.")
        question = input(invite).lower()
    attribut, valeur = question.split(SEPARATEUR)
    return attribut.strip(), valeur.strip()
