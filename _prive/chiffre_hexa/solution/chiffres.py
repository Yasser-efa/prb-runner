"""Valeur des chiffres hexadécimaux."""

CHIFFRES = "0123456789ABCDEF"


def valeur_chiffre(chiffre: str) -> int:
    """
    Calcule la valeur d'un chiffre hexadécimal.

    :param chiffre: le chiffre, en majuscule ou en minuscule
    :return: sa valeur, entre 0 et 15
    """
    return CHIFFRES.index(chiffre.upper())


def chiffre_hexa(valeur: int) -> str:
    """
    Cherche le chiffre hexadécimal qui a une certaine valeur.

    :param valeur: la valeur, entre 0 et 15
    :return: le chiffre, en majuscule
    """
    return CHIFFRES[valeur]
