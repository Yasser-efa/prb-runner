"""Découpage d'une chaine compressée en couples caractère-nombre."""


def obtenir_couples(compresse: str) -> list[tuple[str, int]]:
    """
    Découpe une chaine compressée en couples.

    :param compresse: une suite de caractères suivis de leur nombre de répétitions
    :return: les couples (caractère, nombre), dans l'ordre
    """
    couples = []
    position = 0
    while position < len(compresse):
        caractere = compresse[position]
        debut_nombre = position + 1
        fin_nombre = debut_nombre
        while fin_nombre < len(compresse) and compresse[fin_nombre].isdigit():
            fin_nombre += 1
        couples.append((caractere, int(compresse[debut_nombre:fin_nombre])))
        position = fin_nombre
    return couples
