"""Valeur de nombres écrits dans une base quelconque."""

CHIFFRES = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def est_valide(nombre: str, base: int = 16) -> bool:
    """
    Vérifie si une chaine est un nombre correct dans une base.

    :param nombre: la chaine à vérifier
    :param base: la base, entre 2 et 36
    :return: vrai si la chaine n'est pas vide et n'utilise que des chiffres de la base
    """
    chiffres_permis = CHIFFRES[:base]
    return nombre != "" and all([chiffre in chiffres_permis for chiffre in nombre.upper()])


def valeur_nombre(nombre: str, base: int = 16) -> int:
    """
    Calcule la valeur d'un nombre écrit dans une base.

    :param nombre: le nombre
    :param base: la base, entre 2 et 36
    :return: la valeur du nombre, ou -1 s'il n'est pas valide
    """
    if not est_valide(nombre, base):
        return -1
    valeur = 0
    for chiffre in nombre.upper():
        valeur = valeur * base + CHIFFRES.index(chiffre)
    return valeur
