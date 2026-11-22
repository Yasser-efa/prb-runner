"""Valeur des chiffres hexadécimaux."""

CHIFFRES = "0123456789ABCDEF"


def valeur_chiffre(chiffre: str) -> int:
    """
    Calcule la valeur d'un chiffre hexadécimal.

    :param chiffre: le chiffre, en majuscule ou en minuscule
    :return: sa valeur, entre 0 et 15
    """
    return CHIFFRES.index(chiffre.upper())
