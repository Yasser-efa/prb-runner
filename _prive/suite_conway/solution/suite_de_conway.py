"""Termes de la suite de Conway."""

PREMIER_TERME = "1"


def conway(terme: str) -> str:
    """
    Calcule le terme qui suit un terme de la suite de Conway.

    :param terme: un terme non vide
    :return: le terme suivant
    """
    resultat = ""
    precedent = terme[0]
    compteur = 1
    for symbole in terme[1:]:
        if symbole == precedent:
            compteur += 1
        else:
            resultat += str(compteur) + precedent
            precedent = symbole
            compteur = 1
    return resultat + str(compteur) + precedent


def serie(nb_termes: int) -> list[str]:
    """
    Calcule les premiers termes de la suite de Conway.

    :param nb_termes: le nombre de termes voulus
    :return: les termes, ou une liste vide si nb_termes est inférieur à 1
    """
    if nb_termes < 1:
        return []
    termes = [PREMIER_TERME]
    while len(termes) < nb_termes:
        termes.append(conway(termes[-1]))
    return termes
