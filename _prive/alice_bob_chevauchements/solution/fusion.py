"""Fusion de créneaux qui se chevauchent."""


def fusionner(creneaux: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """
    Rassemble les créneaux qui se chevauchent ou se touchent.

    :param creneaux: des créneaux (début, fin) dans un ordre quelconque
    :return: les créneaux fusionnés, du plus tôt au plus tard
    """
    fusionnes = []
    for debut, fin in sorted(creneaux):
        if not fusionnes or debut > fusionnes[-1][1]:
            fusionnes.append((debut, fin))
        else:
            dernier_debut, derniere_fin = fusionnes[-1]
            fusionnes[-1] = (dernier_debut, max(derniere_fin, fin))
    return fusionnes
