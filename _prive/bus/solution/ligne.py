"""Positions des arrêts d'une ligne de bus."""


def position_arret(numero: int, premier: int = 3, ecart: int = 9) -> int:
    """
    Calcule la position d'un arrêt.

    :param numero: le numéro de l'arrêt, à partir de 1
    :param premier: la position du premier arrêt, en km
    :param ecart: la distance entre deux arrêts, en km
    :return: la position de l'arrêt, en km
    """
    return premier + (numero - 1) * ecart


def numero_arret(position: int, premier: int = 3, ecart: int = 9) -> int:
    """
    Cherche le numéro de l'arrêt situé à une position.

    :param position: la position, en km
    :param premier: la position du premier arrêt, en km
    :param ecart: la distance entre deux arrêts, en km
    :return: le numéro de l'arrêt, ou -1 s'il n'y a pas d'arrêt à cet endroit
    """
    distance = position - premier
    if distance < 0 or distance % ecart != 0:
        return -1
    return distance // ecart + 1


def arrets_entre(debut: int, fin: int, premier: int = 3, ecart: int = 9) -> list[int]:
    """
    Liste les arrêts situés entre deux positions.

    :param debut: la première position, en km
    :param fin: la dernière position, en km
    :param premier: la position du premier arrêt, en km
    :param ecart: la distance entre deux arrêts, en km
    :return: les positions des arrêts, de la plus petite à la plus grande
    """
    return [position for position in range(premier, fin + 1, ecart) if position >= debut]
