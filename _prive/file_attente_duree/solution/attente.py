"""Durées liées à l'évolution d'une file d'attente."""


def minutes_necessaires(depart: int, voulu: int, facteur: int = 2) -> int:
    """
    Calcule la durée nécessaire pour qu'une file atteigne un effectif.

    :param depart: l'effectif de départ, au moins 1
    :param voulu: l'effectif à atteindre
    :param facteur: le nombre par lequel l'effectif est multiplié à chaque minute
    :return: le plus petit nombre de minutes
    """
    effectif = depart
    minutes = 0
    while effectif < voulu:
        effectif *= facteur
        minutes += 1
    return minutes


def premier_depassement(effectifs: list[int], capacite: int) -> int:
    """
    Cherche la première minute à laquelle l'effectif dépasse la capacité.

    :param effectifs: les effectifs relevés minute par minute
    :param capacite: la capacité à ne pas dépasser
    :return: la minute du premier dépassement, ou -1 s'il n'y en a pas
    """
    minute = 0
    while minute < len(effectifs) and effectifs[minute] <= capacite:
        minute += 1
    if minute == len(effectifs):
        return -1
    return minute
