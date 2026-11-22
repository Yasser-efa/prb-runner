"""Décompression d'une chaine."""

from rle.decoupage import obtenir_couples


def decompresser(compresse: str) -> str:
    """
    Retrouve la chaine de départ d'une chaine compressée.

    :param compresse: une suite de caractères suivis de leur nombre de répétitions
    :return: la chaine dans laquelle chaque caractère est répété
    """
    return "".join([caractere * nombre for caractere, nombre in obtenir_couples(compresse)])
