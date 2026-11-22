"""Temps que des personnes peuvent passer ensemble pendant une journée."""


def temps_ensemble(debut_alice: float, fin_alice: float, debut_bob: float, fin_bob: float) -> float:
    """
    Calcule le temps pendant lequel Alice et Bob sont disponibles tous les deux.

    :param debut_alice: heure à laquelle Alice devient disponible
    :param fin_alice: heure à laquelle Alice n'est plus disponible
    :param debut_bob: heure à laquelle Bob devient disponible
    :param fin_bob: heure à laquelle Bob n'est plus disponible
    :return: la durée commune en heures, 0 s'ils ne peuvent pas se voir
    """
    debut_commun = max(debut_alice, debut_bob)
    fin_commune = min(fin_alice, fin_bob)
    return max(0, fin_commune - debut_commun)


def temps_groupe(creneaux: list[tuple[float, float]]) -> float:
    """
    Calcule le temps pendant lequel toutes les personnes d'un groupe sont disponibles.

    :param creneaux: le créneau (début, fin) de chaque personne
    :return: la durée commune en heures, 0 si le groupe ne peut pas se réunir ou est vide
    """
    if not creneaux:
        return 0
    debut_commun = max([debut for debut, _ in creneaux])
    fin_commune = min([fin for _, fin in creneaux])
    return max(0, fin_commune - debut_commun)
