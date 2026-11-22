"""Recherche des créneaux communs à deux personnes."""


def creneaux_communs(
    dispos_alice: list[tuple[int, int]], dispos_bob: list[tuple[int, int]]
) -> list[tuple[int, int]]:
    """
    Cherche les créneaux pendant lesquels Alice et Bob sont disponibles tous les deux.

    :param dispos_alice: les créneaux (début, fin) d'Alice, dans un ordre quelconque
    :param dispos_bob: les créneaux (début, fin) de Bob, dans un ordre quelconque
    :return: les créneaux communs, du plus tôt au plus tard
    """
    communs = []
    for debut_alice, fin_alice in dispos_alice:
        for debut_bob, fin_bob in dispos_bob:
            debut_commun = max(debut_alice, debut_bob)
            fin_commune = min(fin_alice, fin_bob)
            if debut_commun < fin_commune:
                communs.append((debut_commun, fin_commune))
    return sorted(communs)


def temps_ensemble(
    dispos_alice: list[tuple[int, int]], dispos_bob: list[tuple[int, int]]
) -> int:
    """
    Calcule le temps total qu'Alice et Bob peuvent passer ensemble.

    :param dispos_alice: les créneaux (début, fin) d'Alice
    :param dispos_bob: les créneaux (début, fin) de Bob
    :return: la durée totale en heures
    """
    return sum([fin - debut for debut, fin in creneaux_communs(dispos_alice, dispos_bob)])
