"""Calculs sur les jours de la semaine."""

JOURS = ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche")


def jour_apres(jour: str, nb_jours: int) -> str:
    """
    Cherche le jour de la semaine qui vient un certain nombre de jours plus tard.

    :param jour: le jour de départ
    :param nb_jours: le nombre de jours, négatif pour remonter dans le passé
    :return: le nom du jour obtenu
    """
    return JOURS[(JOURS.index(jour) + nb_jours) % len(JOURS)]


def jours_avant(jour: str, jour_voulu: str) -> int:
    """
    Compte les jours à attendre avant le prochain jour voulu.

    :param jour: le jour actuel
    :param jour_voulu: le jour attendu
    :return: le nombre de jours, entre 1 et 7
    """
    ecart = (JOURS.index(jour_voulu) - JOURS.index(jour)) % len(JOURS)
    if ecart == 0:
        return len(JOURS)
    return ecart
