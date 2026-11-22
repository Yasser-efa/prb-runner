"""Jeu de Qui est-ce ? contre l'ordinateur."""

import random

from quiestce.personnages import (PRENOM, creer_personnages, decrire_personnage, filtrer_personnages,
                                  lire_lignes_fichier)
from quiestce.questions import lire_question_utilisateur

ATTRIBUTS = ("lunettes", "chapeau", "yeux clairs", "cheveux foncés", "pilosité faciale", "écharpe")
NB_PERSONNAGES = 36
NB_QUESTIONS = 6
INVITE = "Posez une question (exemple : lunettes = oui) : "


def afficher_personnages(personnages: list[dict[str, str]]) -> None:
    """
    Affiche les personnages restants.

    :param personnages: les personnages à afficher
    """
    print(f"\nIl reste {len(personnages)} personnage(s) :")
    for personnage in personnages:
        print(decrire_personnage(personnage))


def main() -> None:
    """
    Joue une partie de Qui est-ce ?
    """
    tous = creer_personnages(lire_lignes_fichier(), ATTRIBUTS)
    personnages = random.sample(tous, NB_PERSONNAGES)
    mystere = random.choice(personnages)
    print("Bienvenue dans Qui-est-ce ? Essayez de deviner le personnage que j'ai choisi !")
    print("Voici les caractéristiques possibles :")
    print(", ".join(ATTRIBUTS))
    questions_posees = 0
    while len(personnages) > 1 and questions_posees < NB_QUESTIONS:
        afficher_personnages(personnages)
        attribut, _ = lire_question_utilisateur(INVITE, ATTRIBUTS)
        personnages = filtrer_personnages(personnages, attribut, mystere[attribut], True)
        questions_posees += 1
    if len(personnages) == 1:
        print(f"Bravo ! Le personnage est {mystere[PRENOM]}.")
    else:
        print(f"Perdu ! Le personnage était {mystere[PRENOM]}.")


if __name__ == "__main__":
    main()
