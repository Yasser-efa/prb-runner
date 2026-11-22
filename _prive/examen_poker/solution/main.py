"""Jeu du Poker d'As contre l'ordinateur."""

from poker import des as outils_des
from poker.poker_as import analyser_comptage, comparer_tirages, detailler_tirage_des

DIFFICULTE = 3
NB_DES = 5
NB_CHOIX = 3
SELECTION = "-"
INVITE = ">"


def afficher_tirage(des: list[int]) -> None:
    """
    Affiche les initiales des dés d'un tirage ou d'un détail de tirage.

    :param des: les dés à afficher
    """
    print("".join([outils_des.initiale(valeur) for valeur in des]))


def selectionner_des(detail_des: list[int]) -> dict[int, int]:
    """
    Demande au joueur quels dés il veut conserver.

    :param detail_des: le détail du tirage
    :return: le comptage des dés conservés
    """
    print("Veuillez choisir vos dés à l'aide du symbole '-' :")
    print(" " * len(INVITE), end="")
    afficher_tirage(detail_des)
    saisie = input(INVITE)
    conserves = [valeur for valeur, symbole in zip(detail_des, saisie) if symbole == SELECTION]
    return outils_des.compter_des(conserves)


def decrire_combinaison(tirage: list[int]) -> str:
    """
    Écrit le nom de la combinaison d'un tirage.

    :param tirage: un tirage non vide
    :return: par exemple « BRELAN de DAME »
    """
    nombre, valeur = analyser_comptage(outils_des.compter_des(tirage))
    return f"{outils_des.combinaison(nombre)} de {outils_des.figure(valeur)}"


def tirer_ordinateur() -> list[int]:
    """
    Cherche le meilleur de plusieurs tirages.

    :return: le meilleur tirage
    """
    meilleur = outils_des.effectuer_tirage(NB_DES)
    for _ in range(DIFFICULTE - 1):
        tirage = outils_des.effectuer_tirage(NB_DES)
        if comparer_tirages(tirage, meilleur) > 0:
            meilleur = tirage
    return meilleur


def tirer_joueur() -> dict[int, int]:
    """
    Fait jouer le joueur, qui peut conserver des dés entre les lancers.

    :return: le comptage de sa main
    """
    conserves = {}
    tirage = outils_des.effectuer_tirage(NB_DES)
    choix = 0
    while choix < NB_CHOIX and tirage:
        detail = detailler_tirage_des(outils_des.compter_des(tirage))
        conserves = outils_des.somme_comptages(conserves, selectionner_des(detail))
        tirage = outils_des.effectuer_tirage(NB_DES - outils_des.nombre_des(conserves))
        choix += 1
    return outils_des.somme_comptages(conserves, outils_des.compter_des(tirage))


def main() -> None:
    """
    Joue un tour de Poker d'As.
    """
    print("-- Jeu du Poker d'As --\n")
    tirage_ordinateur = tirer_ordinateur()
    print(f"Tirage ordinateur : {decrire_combinaison(tirage_ordinateur)}")
    main_joueur = detailler_tirage_des(tirer_joueur())
    print("\nTirage joueur : ", end="")
    afficher_tirage(main_joueur)
    print(decrire_combinaison(main_joueur))
    resultat = comparer_tirages(main_joueur, tirage_ordinateur)
    if resultat > 0:
        print("Vous gagnez la partie.")
    elif resultat < 0:
        print("Vous perdez la partie.")
    else:
        print("Égalité.")


if __name__ == "__main__":
    main()
