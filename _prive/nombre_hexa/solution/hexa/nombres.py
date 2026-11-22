"""Valeur des nombres hexadécimaux."""

from hexa.chiffres import valeur_chiffre

BASE = 16


def valeur_nombre(nombre: str) -> int:
    """
    Calcule la valeur d'un nombre hexadécimal.

    :param nombre: le nombre, en majuscules ou en minuscules
    :return: sa valeur
    """
    valeur = 0
    for chiffre in nombre:
        valeur = valeur * BASE + valeur_chiffre(chiffre)
    return valeur
