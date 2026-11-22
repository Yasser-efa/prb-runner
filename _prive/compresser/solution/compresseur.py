"""Compression d'une chaine par comptage des caractères répétés."""


def obtenir_couples(chaine: str) -> list[tuple[str, int]]:
    """
    Découpe une chaine en séries de caractères identiques.

    :param chaine: la chaine à découper
    :return: les couples (caractère, nombre de répétitions), dans l'ordre
    """
    if not chaine:
        return []
    couples = []
    precedent = chaine[0]
    compteur = 1
    for caractere in chaine[1:]:
        if caractere == precedent:
            compteur += 1
        else:
            couples.append((precedent, compteur))
            precedent = caractere
            compteur = 1
    couples.append((precedent, compteur))
    return couples


def compresser(chaine: str) -> str:
    """
    Compresse une chaine.

    :param chaine: la chaine à compresser
    :return: chaque caractère suivi de son nombre de répétitions
    """
    return "".join([f"{caractere}{nombre}" for caractere, nombre in obtenir_couples(chaine)])
