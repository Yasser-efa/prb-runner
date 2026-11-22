"""Aide à la décision pour le jeu des damoiselles."""

from damoiselles.damier import captures_possibles, dessiner_damier, position_depart
from damoiselles.pions import PION_BLANC, PION_NOIR, Pion

VIDER, AJOUTER, CALCULER, QUITTER = "1", "2", "3", "4"
MENU = """1. Vider le damier
2. Ajouter des pions
3. Calculer la meilleure prise
4. Quitter"""


def ajouter_pions(positions_pions: dict[int, Pion]) -> None:
    """
    Demande des cases et y ajoute des pions noirs puis blancs.

    :param positions_pions: le pion présent sur chaque case occupée, qui est modifié
    """
    for pion, invite in ((PION_NOIR, "Pions noirs ? "), (PION_BLANC, "Pions blancs ? ")):
        for numero_case in input(invite).split():
            positions_pions[int(numero_case)] = pion


def nombre_captures(prise: str) -> int:
    """
    Compte les pions capturés par une prise.

    :param prise: la description de la prise
    :return: le nombre de pions capturés
    """
    return prise.count("x")


def afficher_meilleure_prise(positions_pions: dict[int, Pion]) -> None:
    """
    Demande une case et affiche la meilleure prise à partir de celle-ci.

    :param positions_pions: le pion présent sur chaque case occupée
    """
    saisie = input("Case départ ? ")
    try:
        prises = captures_possibles(positions_pions, int(saisie))
    except ValueError:
        print("Entrez un entier.")
        return
    if prises:
        print(f"Meilleure capture : {max(prises, key=nombre_captures)}")
    else:
        print("Pas de capture possible !")


def main() -> None:
    """
    Affiche le damier de départ et exécute les opérations du menu.
    """
    print("Bonjour !")
    positions_pions = position_depart()
    dessiner_damier(positions_pions)
    print(MENU)
    choix = input("\nVotre choix ? ")
    while choix != QUITTER:
        if choix == VIDER:
            positions_pions = {}
            print("Damier vidé")
        elif choix == AJOUTER:
            ajouter_pions(positions_pions)
            dessiner_damier(positions_pions)
        elif choix == CALCULER:
            afficher_meilleure_prise(positions_pions)
        else:
            print(MENU)
        choix = input("\nVotre choix ? ")
    print("Au revoir")


if __name__ == "__main__":
    main()
