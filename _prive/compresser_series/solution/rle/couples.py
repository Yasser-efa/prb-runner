"""Découpage d'une chaine en séries de longueur limitée."""


def obtenir_couples(chaine: str, maximum: int = 9) -> list[tuple[str, int]]:
    """
    Découpe une chaine en séries de caractères identiques.

    :param chaine: la chaine à découper
    :param maximum: la longueur maximale d'une série
    :return: les couples (caractère, nombre de répétitions), dans l'ordre
    """
    if not chaine:
        return []
    couples = []
    precedent = chaine[0]
    compteur = 1
    for caractere in chaine[1:]:
        if caractere == precedent and compteur < maximum:
            compteur += 1
        else:
            couples.append((precedent, compteur))
            precedent = caractere
            compteur = 1
    couples.append((precedent, compteur))
    return couples
