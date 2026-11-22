"""Calculs de vitesses moyennes."""


def vitesse_aller_retour(vitesse_aller: float, vitesse_retour: float) -> float:
    """
    Calcule la vitesse moyenne d'un aller-retour par la même route.

    :param vitesse_aller: la vitesse à l'aller, en km/h
    :param vitesse_retour: la vitesse au retour, en km/h
    :return: la vitesse moyenne, en km/h
    """
    return 2 * vitesse_aller * vitesse_retour / (vitesse_aller + vitesse_retour)


def vitesse_moyenne(troncons: list[tuple[float, float]]) -> float:
    """
    Calcule la vitesse moyenne d'un trajet en plusieurs tronçons.

    :param troncons: les tronçons (distance en km, vitesse en km/h)
    :return: la vitesse moyenne, en km/h
    """
    distance_totale = sum([distance for distance, _ in troncons])
    duree_totale = sum([distance / vitesse for distance, vitesse in troncons])
    return distance_totale / duree_totale
