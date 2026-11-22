"""Numérotation des sièges d'une salle."""


def position_siege(siege: int, sieges_par_rangee: int = 20) -> tuple[int, int]:
    """
    Cherche la place d'un siège à partir de son numéro.

    :param siege: le numéro du siège, à partir de 1
    :param sieges_par_rangee: le nombre de sièges d'une rangée
    :return: la rangée et la position dans la rangée, à partir de 1
    """
    place = siege - 1
    return place // sieges_par_rangee + 1, place % sieges_par_rangee + 1


def numero_siege(rangee: int, position: int, sieges_par_rangee: int = 20) -> int:
    """
    Cherche le numéro d'un siège à partir de sa place.

    :param rangee: la rangée, à partir de 1
    :param position: la position dans la rangée, à partir de 1
    :param sieges_par_rangee: le nombre de sièges d'une rangée
    :return: le numéro du siège, à partir de 1
    """
    return (rangee - 1) * sieges_par_rangee + position
