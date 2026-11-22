"""Décompression de chaines formées de couples caractère-chiffre."""

TAILLE_COUPLE = 2


def decompresser(compresse: str) -> str:
    """
    Retrouve la chaine de départ d'une chaine compressée.

    :param compresse: une suite de couples formés d'un caractère et d'un chiffre
    :return: la chaine dans laquelle chaque caractère est répété
    """
    resultat = ""
    for debut in range(0, len(compresse), TAILLE_COUPLE):
        caractere, repetitions = compresse[debut:debut + TAILLE_COUPLE]
        resultat += caractere * int(repetitions)
    return resultat


def taille_decompressee(compresse: str) -> int:
    """
    Calcule la longueur de la chaine décompressée, sans la construire.

    :param compresse: une suite de couples formés d'un caractère et d'un chiffre
    :return: le nombre de caractères de la chaine décompressée
    """
    return sum([int(chiffre) for chiffre in compresse[1::TAILLE_COUPLE]])
