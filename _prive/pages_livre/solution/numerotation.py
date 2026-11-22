"""Chiffres imprimés pour numéroter les pages d'un livre."""


def nombre_chiffres(nb_pages: int) -> int:
    """
    Compte les chiffres à imprimer pour numéroter toutes les pages d'un livre.

    :param nb_pages: le nombre de pages du livre
    :return: le nombre de chiffres
    """
    return chiffres_entre(1, nb_pages)


def chiffres_entre(premiere: int, derniere: int) -> int:
    """
    Compte les chiffres à imprimer pour numéroter une partie des pages.

    :param premiere: la première page à numéroter
    :param derniere: la dernière page à numéroter
    :return: le nombre de chiffres
    """
    return sum([len(str(page)) for page in range(premiere, derniere + 1)])


def occurrences(chiffre: int, nb_pages: int) -> int:
    """
    Compte le nombre de fois qu'un chiffre est imprimé.

    :param chiffre: le chiffre, entre 0 et 9
    :param nb_pages: le nombre de pages du livre
    :return: le nombre de fois que le chiffre est imprimé
    """
    return sum([str(page).count(str(chiffre)) for page in range(1, nb_pages + 1)])
