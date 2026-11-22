"""Évolution d'une file d'attente."""


def effectif_depart(effectif_final: int, minutes: int, facteur: int = 2) -> int:
    """
    Retrouve l'effectif de départ d'une file d'attente.

    :param effectif_final: l'effectif à la fin
    :param minutes: le nombre de minutes écoulées
    :param facteur: le nombre par lequel l'effectif est multiplié à chaque minute
    :return: l'effectif de départ, ou -1 si aucun effectif entier ne convient
    """
    croissance = facteur ** minutes
    if effectif_final % croissance != 0:
        return -1
    return effectif_final // croissance


def evolution(depart: int, minutes: int, facteur: int = 2) -> list[int]:
    """
    Calcule les effectifs successifs d'une file d'attente.

    :param depart: l'effectif de départ
    :param minutes: le nombre de minutes écoulées
    :param facteur: le nombre par lequel l'effectif est multiplié à chaque minute
    :return: les effectifs, du départ à la dernière minute comprise
    """
    return [depart * facteur ** minute for minute in range(minutes + 1)]
