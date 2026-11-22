"""Pages d'un livre retrouvées à partir des chiffres imprimés."""


def page_du_chiffre(rang: int) -> int:
    """
    Cherche la page sur laquelle se trouve un chiffre imprimé.

    :param rang: le rang du chiffre, à partir de 1
    :return: le numéro de la page
    """
    page = 0
    chiffres_imprimes = 0
    while chiffres_imprimes < rang:
        page += 1
        chiffres_imprimes += len(str(page))
    return page


def nombre_pages(nb_chiffres: int) -> int:
    """
    Cherche le nombre de pages d'un livre à partir du nombre de chiffres imprimés.

    :param nb_chiffres: le nombre de chiffres imprimés
    :return: le nombre de pages, ou -1 si aucun livre ne convient
    """
    page = 0
    chiffres_imprimes = 0
    while chiffres_imprimes < nb_chiffres:
        page += 1
        chiffres_imprimes += len(str(page))
    if chiffres_imprimes == nb_chiffres:
        return page
    return -1
