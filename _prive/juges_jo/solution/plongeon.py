"""Calcul de la note d'un plongeon à partir des notes des juges."""


def note_finale(notes: list[float]) -> float:
    """
    Calcule la note finale d'un plongeon, sans la meilleure ni la moins bonne note.

    :param notes: les notes des juges
    :return: la moyenne des notes conservées
    """
    return note_ajustee(notes)


def note_ajustee(notes: list[float], nb_retirees: int = 1) -> float:
    """
    Calcule la moyenne des notes après avoir retiré les extrêmes.

    :param notes: les notes des juges
    :param nb_retirees: le nombre de notes à retirer de chaque côté
    :return: la moyenne des notes conservées
    """
    conservees = sorted(notes)[nb_retirees:len(notes) - nb_retirees]
    return sum(conservees) / len(conservees)
