"""Damier du jeu des damoiselles : dessin et recherche des prises."""

from damoiselles.pions import (PION_BLANC, PION_NOIR, Pion, contenu_case, est_case_vide,
                               est_occupee, sont_couleurs_differentes)

HAUTEUR, LARGEUR = 10, 10
CASE_NOIRE = "█" * 3
CASES_PAR_LIGNE = LARGEUR // 2
NB_CASES = HAUTEUR * CASES_PAR_LIGNE
NB_PIONS = 20
ARRIVEE_IMPOSSIBLE = -1


def est_blanche(ligne: int, colonne: int) -> bool:
    """
    Vérifie si une case du damier est blanche.

    :param ligne: la ligne de la case
    :param colonne: la colonne de la case
    :return: vrai si la case est blanche
    """
    return (ligne + colonne) % 2 == 1


def obtenir_numero(ligne: int, colonne: int) -> int:
    """
    Calcule le numéro d'une case blanche.

    :param ligne: la ligne de la case
    :param colonne: la colonne de la case
    :return: le numéro de la case
    """
    return ligne * CASES_PAR_LIGNE + colonne // 2


def obtenir_position(numero_case: int) -> tuple[int, int]:
    """
    Calcule la ligne et la colonne d'une case blanche.

    :param numero_case: le numéro de la case
    :return: la ligne et la colonne
    """
    ligne = numero_case // CASES_PAR_LIGNE
    colonne = numero_case % CASES_PAR_LIGNE * 2
    if est_blanche(ligne, colonne):
        return ligne, colonne
    return ligne, colonne + 1


def dessiner_damier(positions_pions: dict[int, Pion]) -> None:
    """
    Dessine le damier avec ses pions et les numéros des cases vides.

    :param positions_pions: le pion présent sur chaque case occupée
    """
    for ligne in range(HAUTEUR):
        for colonne in range(LARGEUR):
            numero_case = obtenir_numero(ligne, colonne)
            if not est_blanche(ligne, colonne):
                print(CASE_NOIRE, end="")
            elif est_occupee(positions_pions, numero_case):
                print(contenu_case(positions_pions, numero_case), end="")
            else:
                print(f"{numero_case:3}", end="")
        print()


def position_depart() -> dict[int, Pion]:
    """
    Crée la position des pions en début de partie.

    :return: le pion présent sur chaque case occupée
    """
    positions_pions = {}
    for numero_case in range(NB_PIONS):
        positions_pions[numero_case] = PION_NOIR
        positions_pions[NB_CASES - NB_PIONS + numero_case] = PION_BLANC
    return positions_pions


def voisines(numero_case: int) -> set[int]:
    """
    Cherche les cases voisines d'une case, en diagonale.

    :param numero_case: le numéro de la case
    :return: les numéros des cases voisines
    """
    ligne, colonne = obtenir_position(numero_case)
    resultat = set()
    for autre_ligne in (ligne - 1, ligne + 1):
        for autre_colonne in (colonne - 1, colonne + 1):
            if 0 <= autre_ligne < HAUTEUR and 0 <= autre_colonne < LARGEUR:
                resultat.add(obtenir_numero(autre_ligne, autre_colonne))
    return resultat


def arrivee_capture(depart: int, prise: int) -> int:
    """
    Calcule la case d'arrivée d'un pion qui en prend un autre.

    :param depart: la case du pion qui se déplace
    :param prise: la case du pion qui est pris
    :return: la case d'arrivée, ou -1 si la prise est impossible
    """
    if prise not in voisines(depart):
        return ARRIVEE_IMPOSSIBLE
    ligne_depart, colonne_depart = obtenir_position(depart)
    for candidate in voisines(prise):
        ligne, colonne = obtenir_position(candidate)
        if ligne != ligne_depart and colonne != colonne_depart:
            return candidate
    return ARRIVEE_IMPOSSIBLE


def decrire_prise(etapes: list[int]) -> str:
    """
    Écrit une prise sous la forme « 27x18x7 ».

    :param etapes: les cases successives du pion
    :return: la description de la prise
    """
    return "x".join([str(etape) for etape in etapes])


def captures_possibles(positions_pions: dict[int, Pion], depart: int) -> set[str]:
    """
    Cherche toutes les prises possibles à partir d'une case.

    :param positions_pions: le pion présent sur chaque case occupée
    :param depart: la case du pion qui se déplace
    :return: les descriptions des prises simples et multiples
    """
    resultat = set()
    prises_a_explorer = [[depart]]
    while prises_a_explorer:
        etapes = prises_a_explorer.pop()
        for voisine in voisines(etapes[-1]):
            arrivee = arrivee_capture(etapes[-1], voisine)
            if (arrivee != ARRIVEE_IMPOSSIBLE and arrivee not in etapes
                    and sont_couleurs_differentes(positions_pions, voisine, depart)
                    and est_case_vide(positions_pions, arrivee)):
                nouvelles_etapes = etapes + [arrivee]
                description = decrire_prise(nouvelles_etapes)
                if description not in resultat:
                    resultat.add(description)
                    prises_a_explorer.append(nouvelles_etapes)
    return resultat
