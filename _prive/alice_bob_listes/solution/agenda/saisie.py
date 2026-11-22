"""Lecture des disponibilités tapées par l'utilisateur."""


def lire_creneaux(texte: str) -> list[tuple[int, int]]:
    """
    Lit des créneaux écrits sous la forme « début-fin ».

    :param texte: les créneaux, séparés par une ou plusieurs espaces
    :return: les créneaux (début, fin), dans le même ordre
    """
    creneaux = []
    for morceau in texte.split():
        debut, fin = morceau.split("-")
        creneaux.append((int(debut), int(fin)))
    return creneaux
