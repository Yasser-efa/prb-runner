"""Écriture d'un entier dans une base."""

CHIFFRES = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE_HEXA = 16


def entier_vers_base(valeur: int, base: int = 16) -> str:
    """
    Écrit un entier dans une base.

    :param valeur: l'entier, positif ou nul
    :param base: la base, entre 2 et 36
    :return: l'écriture de l'entier, en majuscules
    """
    if valeur == 0:
        return CHIFFRES[0]
    resultat = ""
    reste_a_ecrire = valeur
    while reste_a_ecrire > 0:
        resultat = CHIFFRES[reste_a_ecrire % base] + resultat
        reste_a_ecrire //= base
    return resultat


def entier_vers_hexa(valeur: int) -> str:
    """
    Écrit un entier en hexadécimal.

    :param valeur: l'entier, positif ou nul
    :return: l'écriture hexadécimale, en majuscules
    """
    return entier_vers_base(valeur, BASE_HEXA)
