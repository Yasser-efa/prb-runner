"""Compression d'une chaine avec un seul chiffre par série."""

from rle.couples import obtenir_couples


def compresser(chaine: str) -> str:
    """
    Compresse une chaine.

    :param chaine: la chaine à compresser
    :return: les caractères suivis de leur nombre de répétitions, entre 1 et 9
    """
    return "".join([f"{caractere}{nombre}" for caractere, nombre in obtenir_couples(chaine)])


def meilleure_forme(chaine: str) -> str:
    """
    Choisit la forme la plus courte d'une chaine.

    :param chaine: la chaine de départ
    :return: la version compressée si elle est plus courte, sinon la chaine elle-même
    """
    compressee = compresser(chaine)
    if len(compressee) < len(chaine):
        return compressee
    return chaine
