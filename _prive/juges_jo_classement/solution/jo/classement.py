"""Classement des plongeurs."""

from jo.notes import note_finale

PLACES_PODIUM = 3


def cle_de_tri(ligne: tuple[str, float]) -> tuple[float, str]:
    """
    Donne la clé de tri d'une ligne du classement.

    :param ligne: le nom et la note d'un plongeur
    :return: la note opposée puis le nom, pour trier par note décroissante
    """
    nom, note = ligne
    return -note, nom


def classer(resultats: dict[str, list[float]]) -> list[tuple[str, float]]:
    """
    Classe les plongeurs de la meilleure note à la moins bonne.

    :param resultats: les notes des juges pour chaque plongeur
    :return: les noms et les notes finales, par ordre alphabétique en cas d'égalité
    """
    lignes = [(nom, note_finale(notes)) for nom, notes in resultats.items()]
    return sorted(lignes, key=cle_de_tri)


def podium(resultats: dict[str, list[float]]) -> list[str]:
    """
    Cherche les trois meilleurs plongeurs.

    :param resultats: les notes des juges pour chaque plongeur
    :return: les noms des trois premiers, ou de tous s'ils sont moins nombreux
    """
    return [nom for nom, _ in classer(resultats)[:PLACES_PODIUM]]
