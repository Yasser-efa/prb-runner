"""Distance parcourue par un taxi dans une ville en damier."""


def distance_taxi(depart: tuple[int, int], arrivee: tuple[int, int]) -> int:
    """
    Calcule la distance parcourue par un taxi qui suit les rues.

    :param depart: le carrefour de départ
    :param arrivee: le carrefour d'arrivée
    :return: la distance du plus court chemin
    """
    return abs(arrivee[0] - depart[0]) + abs(arrivee[1] - depart[1])
