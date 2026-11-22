"""Temps commun à deux personnes."""

from fusion import fusionner


def temps_ensemble(
    dispos_alice: list[tuple[int, int]], dispos_bob: list[tuple[int, int]]
) -> int:
    """
    Calcule le temps pendant lequel Alice et Bob sont disponibles tous les deux.

    :param dispos_alice: les créneaux (début, fin) d'Alice
    :param dispos_bob: les créneaux (début, fin) de Bob
    :return: la durée totale en heures
    """
    total = 0
    for debut_alice, fin_alice in fusionner(dispos_alice):
        for debut_bob, fin_bob in fusionner(dispos_bob):
            total += max(0, min(fin_alice, fin_bob) - max(debut_alice, debut_bob))
    return total
