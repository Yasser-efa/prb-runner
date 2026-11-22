"""Jeu de Slam : retrouver les mots d'une grille."""

import re

from slam import exemples
from slam.colonnes_positions import MOT, positions_mot
from slam.grille_mots import afficher_grille, chercher_mots_grille, numeroter_grille

ESSAIS_SUPPLEMENTAIRES = 3
FORMAT_PROPOSITION = r"[1-9] [A-Z]{2,}"
INVITE = "Entrez un numéro suivi d'un mot : "


def lire_proposition() -> tuple[int, str]:
    """
    Demande une proposition jusqu'à ce que son format soit correct.

    :return: le numéro et le mot proposés
    """
    saisie = input(INVITE)
    while not re.fullmatch(FORMAT_PROPOSITION, saisie):
        saisie = input(INVITE)
    numero, mot = saisie.split()
    return int(numero), mot


def est_correcte(numero: int, mot: str, mots: list[dict]) -> bool:
    """
    Vérifie une proposition.

    :param numero: le numéro proposé, à partir de 1
    :param mot: le mot proposé
    :param mots: les mots de la grille
    :return: vrai si le mot est celui qui porte ce numéro
    """
    return numero <= len(mots) and mots[numero - 1][MOT] == list(mot)


def main() -> None:
    """
    Joue une partie de Slam.
    """
    grille = exemples.ENONCE
    mots = chercher_mots_grille(grille)
    numeroter_grille(grille, mots)
    essais = len(mots) + ESSAIS_SUPPLEMENTAIRES
    numeros_trouves = set()
    positions_trouvees = set()
    print("Bienvenue dans Slam sur France 3 !")
    print(f"Il y a {len(mots)} mots à trouver, vous avez {essais} essais.")
    afficher_grille(grille, positions_trouvees)
    while essais > 0 and len(numeros_trouves) < len(mots):
        numero, mot = lire_proposition()
        essais -= 1
        if not est_correcte(numero, mot, mots):
            print(f"{mot} : ce mot n'est pas correct.")
        elif numero in numeros_trouves:
            print(f"{mot} : ce mot a déjà été trouvé.")
        else:
            numeros_trouves.add(numero)
            positions_trouvees |= positions_mot(mots[numero - 1])
            afficher_grille(grille, positions_trouvees)
            print()
    if len(numeros_trouves) == len(mots):
        print("Bravo, vous avez gagné !")
    else:
        print("Dommage, vous avez perdu.")


if __name__ == "__main__":
    main()
