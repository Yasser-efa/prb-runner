"""Distance parcourue par un drone et comparaison avec un taxi."""

import math

from distances.taxi import distance_taxi


def distance_drone(depart: tuple[int, int], arrivee: tuple[int, int]) -> float:
    """
    Calcule la distance parcourue par un drone en ligne droite.

    :param depart: le carrefour de départ
    :param arrivee: le carrefour d'arrivée
    :return: la distance à vol d'oiseau
    """
    return math.sqrt((arrivee[0] - depart[0]) ** 2 + (arrivee[1] - depart[1]) ** 2)


def gain_drone(depart: tuple[int, int], arrivee: tuple[int, int]) -> float:
    """
    Calcule la distance que le drone économise par rapport au taxi.

    :param depart: le carrefour de départ
    :param arrivee: le carrefour d'arrivée
    :return: la différence entre les deux distances
    """
    return distance_taxi(depart, arrivee) - distance_drone(depart, arrivee)
