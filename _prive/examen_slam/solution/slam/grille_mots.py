"""Recherche, numérotation et affichage des mots d'une grille."""

from slam.colonnes_positions import DEBUT, MOT, NOTE, obtenir_colonne

ESPACE = " "
LETTRE_CACHEE = "_"
LONGUEUR_MINIMALE = 2
HORIZONTAL = "H"
VERTICAL = "V"


def chercher_mots_ligne(ligne: list[str], numero: int, note: str) -> list[dict]:
    """
    Cherche les mots d'au moins deux lettres dans une ligne.

    :param ligne: les caractères de la ligne
    :param numero: le numéro de la ligne ou de la colonne
    :param note: la note à associer aux mots trouvés
    :return: les mots trouvés, de gauche à droite
    """
    mots = []
    debut = 0
    for index, caractere in enumerate(ligne + [ESPACE]):
        if caractere == ESPACE:
            if index - debut >= LONGUEUR_MINIMALE:
                mots.append({MOT: ligne[debut:index], DEBUT: (numero, debut), NOTE: note})
            debut = index + 1
    return mots


def chercher_mots_grille(grille: list[list[str]]) -> list[dict]:
    """
    Cherche les mots horizontaux puis verticaux d'une grille.

    :param grille: les lignes de la grille
    :return: les mots trouvés
    """
    mots = []
    for numero_ligne, ligne in enumerate(grille):
        mots += chercher_mots_ligne(ligne, numero_ligne, HORIZONTAL)
    for numero_colonne in range(len(grille[0])):
        colonne = obtenir_colonne(grille, numero_colonne)
        mots += chercher_mots_ligne(colonne, numero_colonne, VERTICAL)
    return mots


def numeroter_grille(grille: list[list[str]], liste_mots: list[dict]) -> None:
    """
    Écrit dans la grille le numéro de chaque mot, devant sa première lettre.

    :param grille: les lignes de la grille, qui sont modifiées
    :param liste_mots: les mots à numéroter
    """
    for numero, mot in enumerate(liste_mots, 1):
        if mot[NOTE] == HORIZONTAL:
            ligne, colonne = mot[DEBUT]
            grille[ligne][colonne - 1] = str(numero)
        else:
            colonne, ligne = mot[DEBUT]
            grille[ligne - 1][colonne] = str(numero)


def afficher_grille(grille: list[list[str]], positions_trouvees: set[tuple[int, int]]) -> None:
    """
    Affiche une grille en cachant les lettres qui n'ont pas été trouvées.

    :param grille: les lignes de la grille
    :param positions_trouvees: les positions des lettres à montrer
    """
    for numero_ligne, ligne in enumerate(grille):
        for numero_colonne, caractere in enumerate(ligne):
            if caractere.isalpha() and (numero_ligne, numero_colonne) not in positions_trouvees:
                print(LETTRE_CACHEE, end="")
            else:
                print(caractere, end="")
        print()
