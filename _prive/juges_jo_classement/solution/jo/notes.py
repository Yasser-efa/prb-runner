"""Calcul de la note d'un plongeon."""


def note_finale(notes: list[float]) -> float:
    """
    Calcule la note finale d'un plongeon, sans la meilleure ni la moins bonne note.

    :param notes: les notes des juges, au moins trois
    :return: la moyenne des notes conservées
    """
    conservees = sorted(notes)[1:-1]
    return sum(conservees) / len(conservees)
