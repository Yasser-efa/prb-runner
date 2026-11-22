"""Lampes d'une guirlande qui s'allument à intervalles réguliers."""


def toutes_allumees(periodes: list[int], minute: int) -> bool:
    """
    Vérifie si toutes les lampes s'allument à un instant donné.

    :param periodes: la période de chaque lampe, en minutes
    :param minute: l'instant à vérifier
    :return: vrai si toutes les lampes s'allument à cette minute
    """
    return all([minute % periode == 0 for periode in periodes])


def duree_rallumage(periodes: list[int]) -> int:
    """
    Cherche la première minute à laquelle toutes les lampes se rallument ensemble.

    :param periodes: la période de chaque lampe, en minutes
    :return: la durée depuis l'allumage de la guirlande, en minutes
    """
    plus_longue = max(periodes)
    minute = plus_longue
    while not toutes_allumees(periodes, minute):
        minute += plus_longue
    return minute


def instants_communs(periodes: list[int], limite: int) -> list[int]:
    """
    Liste les minutes auxquelles toutes les lampes s'allument ensemble.

    :param periodes: la période de chaque lampe, en minutes
    :param limite: la dernière minute à examiner
    :return: les minutes, de la plus petite à la plus grande
    """
    return [minute for minute in range(1, limite + 1) if toutes_allumees(periodes, minute)]
