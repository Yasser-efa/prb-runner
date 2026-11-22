"""Lampes d'une guirlande qui changent d'état à intervalles réguliers."""


def lampe_allumee(periode: int, minute: int) -> bool:
    """
    Vérifie si une lampe est allumée à un instant donné.

    :param periode: la durée entre deux changements d'état, en minutes
    :param minute: l'instant à vérifier
    :return: vrai si la lampe est allumée à cette minute
    """
    return minute // periode % 2 == 0


def toutes_allumees(periodes: list[int], minute: int) -> bool:
    """
    Vérifie si toutes les lampes sont allumées à un instant donné.

    :param periodes: la période de chaque lampe, en minutes
    :param minute: l'instant à vérifier
    :return: vrai si toutes les lampes sont allumées à cette minute
    """
    return all([lampe_allumee(periode, minute) for periode in periodes])


def duree_rallumage(periodes: list[int]) -> int:
    """
    Cherche la première minute à laquelle toutes les lampes sont à nouveau allumées.

    :param periodes: la période de chaque lampe, en minutes
    :return: la durée depuis l'allumage de la guirlande, en minutes
    """
    minute = min(periodes)
    while not toutes_allumees(periodes, minute):
        minute += 1
    return minute
