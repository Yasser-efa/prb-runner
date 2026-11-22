"""Trajets de taxis dans une ville en damier."""


def distance_taxi(depart: tuple[int, int], arrivee: tuple[int, int]) -> int:
    """
    Calcule la distance entre deux carrefours en suivant les rues.

    :param depart: le carrefour de départ
    :param arrivee: le carrefour d'arrivée
    :return: la distance du plus court chemin
    """
    return abs(arrivee[0] - depart[0]) + abs(arrivee[1] - depart[1])


def lire_etapes(texte: str) -> list[tuple[int, int]]:
    """
    Lit des carrefours écrits sous la forme « x,y ».

    :param texte: les carrefours, séparés par une ou plusieurs espaces
    :return: les carrefours, dans le même ordre
    """
    etapes = []
    for morceau in texte.split():
        abscisse, ordonnee = morceau.split(",")
        etapes.append((int(abscisse), int(ordonnee)))
    return etapes


def distance_trajet(etapes: list[tuple[int, int]]) -> int:
    """
    Calcule la longueur d'un trajet qui passe par plusieurs carrefours.

    :param etapes: les carrefours, dans l'ordre du trajet
    :return: la distance totale, 0 s'il y a moins de deux étapes
    """
    return sum([distance_taxi(depart, arrivee) for depart, arrivee in zip(etapes, etapes[1:])])


def taxi_le_plus_proche(client: tuple[int, int], taxis: list[tuple[int, int]]) -> int:
    """
    Cherche le taxi le plus proche d'un client.

    :param client: le carrefour où se trouve le client
    :param taxis: les carrefours où se trouvent les taxis
    :return: l'indice du taxi le plus proche, ou -1 s'il n'y a pas de taxi
    """
    if not taxis:
        return -1
    distances = [distance_taxi(client, taxi) for taxi in taxis]
    return distances.index(min(distances))
