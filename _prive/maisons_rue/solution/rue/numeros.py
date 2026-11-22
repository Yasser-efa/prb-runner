"""Comptage des maisons entre deux numéros."""

COTES = 2


def maisons_quai(premier: int, dernier: int, bornes_comprises: bool = True) -> int:
    """
    Compte les maisons situées entre deux numéros d'un quai.

    :param premier: un des deux numéros
    :param dernier: l'autre numéro
    :param bornes_comprises: vrai si les deux maisons données comptent aussi
    :return: le nombre de maisons
    """
    intervalles = abs(dernier - premier)
    if bornes_comprises:
        return intervalles + 1
    return max(0, intervalles - 1)


def maisons_rue(premier: int, dernier: int, bornes_comprises: bool = True) -> int:
    """
    Compte les maisons situées entre deux numéros, du même côté d'une rue.

    :param premier: un des deux numéros
    :param dernier: l'autre numéro
    :param bornes_comprises: vrai si les deux maisons données comptent aussi
    :return: le nombre de maisons, ou -1 si les numéros ne sont pas du même côté
    """
    ecart = abs(dernier - premier)
    if ecart % COTES != 0:
        return -1
    return maisons_quai(0, ecart // COTES, bornes_comprises)
