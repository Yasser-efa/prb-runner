"""Analyse et comparaison de tirages du Poker d'As."""

from poker.des import compter_des

SEPARATEUR = 0


def analyser_comptage(comptage: dict[int, int]) -> tuple[int, int]:
    """
    Cherche la combinaison la plus forte d'un comptage.

    :param comptage: un comptage de dés non vide
    :return: le nombre de dés de la combinaison et la valeur de ces dés
    """
    return max([(nombre, valeur) for valeur, nombre in comptage.items()])


def comparer_tirages(tirage1: list[int], tirage2: list[int]) -> int:
    """
    Compare la force de deux tirages.

    :param tirage1: le premier tirage, non vide
    :param tirage2: le second tirage, non vide
    :return: un entier positif si le premier est meilleur, négatif si c'est le second, sinon 0
    """
    force1 = analyser_comptage(compter_des(tirage1))
    force2 = analyser_comptage(compter_des(tirage2))
    if force1 > force2:
        return 1
    if force1 < force2:
        return -1
    return 0


def detailler_tirage_des(comptage: dict[int, int]) -> list[int]:
    """
    Construit le détail d'un tirage : les dés triés, avec des zéros entre les valeurs différentes.

    :param comptage: un comptage de dés non vide
    :return: le détail du tirage
    """
    detail = []
    for valeur in sorted(comptage):
        if detail:
            detail.append(SEPARATEUR)
        detail += [valeur] * comptage[valeur]
    return detail
