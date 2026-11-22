"""Recherche d'une boule plus lourde avec une balance à plateaux."""

ISSUES_PESEE = 3


def nombre_pesees(nb_boules: int) -> int:
    """
    Calcule le nombre de pesées qui suffit toujours à trouver la boule la plus lourde.

    :param nb_boules: le nombre de boules, au moins 1
    :return: le plus petit nombre de pesées
    """
    pesees = 0
    capacite = 1
    while capacite < nb_boules:
        capacite *= ISSUES_PESEE
        pesees += 1
    return pesees


def boules_maximum(nb_pesees: int) -> int:
    """
    Calcule le plus grand nombre de boules que l'on peut départager.

    :param nb_pesees: le nombre de pesées autorisées
    :return: le nombre maximum de boules
    """
    return ISSUES_PESEE ** nb_pesees
