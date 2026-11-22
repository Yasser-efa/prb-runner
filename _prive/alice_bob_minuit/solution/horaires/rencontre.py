"""Temps commun à deux créneaux quotidiens."""

from horaires.decoupage import decouper


def temps_ensemble(debut_alice: float, fin_alice: float, debut_bob: float, fin_bob: float) -> float:
    """
    Calcule le temps pendant lequel deux créneaux quotidiens ont lieu en même temps.

    :param debut_alice: l'heure de début du créneau d'Alice
    :param fin_alice: l'heure de fin du créneau d'Alice
    :param debut_bob: l'heure de début du créneau de Bob
    :param fin_bob: l'heure de fin du créneau de Bob
    :return: le nombre d'heures communes par jour
    """
    total = 0
    for debut_a, fin_a in decouper(debut_alice, fin_alice):
        for debut_b, fin_b in decouper(debut_bob, fin_bob):
            total += max(0, min(fin_a, fin_b) - max(debut_a, debut_b))
    return total
