"""Création et filtrage des personnages du jeu."""

import random

CHEMIN_PRENOMS = "donnees/prenoms.txt"
PRENOM = "prenom"
OUI, NON = "oui", "non"


def lire_lignes_fichier(chemin_fichier: str = CHEMIN_PRENOMS) -> list[str]:
    """
    Lit les lignes d'un fichier.

    :param chemin_fichier: le chemin du fichier
    :return: les lignes sans retour à la ligne, ou une liste vide en cas de problème
    """
    try:
        with open(chemin_fichier, encoding="utf-8") as fichier:
            return [ligne.rstrip("\n") for ligne in fichier]
    except OSError:
        return []


def creer_personnages(prenoms: list[str], attributs: tuple[str, ...]) -> list[dict[str, str]]:
    """
    Crée un personnage pour chaque combinaison d'attributs.

    :param prenoms: les prénoms disponibles
    :param attributs: les attributs des personnages
    :return: les personnages, avec des prénoms choisis au hasard
    """
    if not attributs:
        return []
    nombre_lignes = 2 ** len(attributs)
    personnages = []
    for ligne, prenom in enumerate(random.sample(prenoms, nombre_lignes)):
        personnage = {PRENOM: prenom}
        for attribut, bit in zip(attributs, f"{ligne:0{len(attributs)}b}"):
            personnage[attribut] = OUI if bit == "1" else NON
        personnages.append(personnage)
    return personnages


def decrire_personnage(personnage: dict[str, str]) -> str:
    """
    Écrit un personnage et ses attributs.

    :param personnage: le personnage à décrire
    :return: son prénom, suivi des attributs qu'il possède
    """
    presents = [cle for cle, valeur in personnage.items() if valeur == OUI and cle != PRENOM]
    if presents:
        return f"{personnage[PRENOM]} : {', '.join(presents)}."
    return f"{personnage[PRENOM]}."


def filtrer_personnages(
    personnages: list[dict[str, str]], attribut: str, valeur: str, conserver: bool
) -> list[dict[str, str]]:
    """
    Garde les personnages dont un attribut a une certaine valeur, ou les autres.

    :param personnages: les personnages à filtrer
    :param attribut: l'attribut à examiner
    :param valeur: la valeur recherchée
    :param conserver: vrai pour garder les personnages qui ont cette valeur, faux pour les autres
    :return: une nouvelle liste de personnages, dans le même ordre
    """
    return [
        personnage for personnage in personnages
        if attribut not in personnage or (personnage[attribut] == valeur) == conserver
    ]
