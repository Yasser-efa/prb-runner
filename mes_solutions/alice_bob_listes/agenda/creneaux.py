def creneaux_communs(dispos_alice: list[tuple[int, int]], dispos_bob: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """
    Renvoie les créneaux communs d'Alice et Bob, du plus tôt au plus tard.
    Un créneau commun a une durée d'au moins 1h.

    :param dispos_alice: liste des créneaux d'Alice
    :param dispos_bob: liste des créneaux de Bob
    :return: liste triée des créneaux communs
    """
    communs = []
    for a_debut, a_fin in dispos_alice:
        for b_debut, b_fin in dispos_bob:
            debut = max(a_debut, b_debut)
            fin = min(a_fin, b_fin)
            if fin - debut >= 1:
                communs.append((debut, fin))
    return sorted(communs)


def temps_ensemble(dispos_alice, dispos_bob):
    creneaux = creneaux_communs(dispos_alice, dispos_bob)
    return sum(creneau[1] - creneau[0] for creneau in creneaux)


if __name__ == "__main__":
    print(temps_ensemble([(9, 12), (14, 17)], [(11, 15)]))
