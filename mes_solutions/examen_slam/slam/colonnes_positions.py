"""
Manipulations des colonnes et positions d'une grille.
Le format de la documentation est différent, mais reste compréhensible et est correctement interprété par Pycharm.

NE RECOPIEZ NI NE MODIFIEZ CE CODE SOUS AUCUN PRÉTEXTE.

Author:
    Simon Liénardy
"""
from typing import Any
from slam.fonctions import f1, f2, f6

MOT = "mot"
DEBUT = "debut"
NOTE = "note"


def obtenir_colonne(grille: list[list], no_colonne: int) -> list:
    """Obtenir une colonne d'une grille

    Arguments:
        grille: Une liste de liste (formant un tableau à deux dimensions).
        no_colonne: Un numéro de colonne
    Return:
        La colonne demandée
    """
    assert 0 <= no_colonne < len(grille[0]), "Le numero de colonne n'existe pas dans cette grille. FAITES UN DESSIN !!!"
    return f1(grille, no_colonne)


def ecrire_colonne(grille: list[list], no_colonne: int, colonne: list) -> list[list]:
    """Écrire une colonne dans un tableau 2D.

    Arguments:
        grille: Une liste de liste (formant un tableau à deux dimensions).
        no_colonne: Un numéro de colonne.
        colonne: Une liste contenant les éléments à écrire dans la colonne.

    Return:
        La grille après que la modification a été effectuée.
    """
    return f2(grille, no_colonne, colonne)


def positions_mot(mot: dict[str, Any]) -> set[tuple[int, int]]:
    """Retourne les positions occupées par un mot, sous la forme d'un ensemble

    Un mot est représenté par un dictionnaire possédant les clés suivantes (donc comme dans l'énoncé...):
        - 'mot' : une liste de caractère
        - 'debut' : un tuple (i, j) représentant la position de la première lettre du mot
        - 'note' : une valeur qui est soit 'H' ou 'V'

    Exemples:
        {'mot': 'ABC', 'debut': (1, 2), 'H'} -> {(1, 2), (1, 3), (1, 4)}
        {'mot': 'ABCD', 'debut': (1, 2), 'V'} -> {(2, 1), (3, 1), (4, 1), (5, 1)}


    Arguments:
        mot: Un dictionnaire décrit ci-dessus.

    Return:
        Un ensemble contenant les positions occupées par le mot, déduites des informations données.
    """
    assert len(mot[DEBUT]) == 2, "La valeur debut DOIT être un tuple de longueur 2 !"
    assert mot[NOTE] == 'V' or mot[NOTE] == 'H', "La valeur note DOIT être V ou H !"

    return f6(mot[MOT], mot[DEBUT], mot[NOTE])
