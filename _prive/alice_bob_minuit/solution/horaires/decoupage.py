"""Découpage de créneaux quotidiens à minuit."""

MINUIT_DEBUT = 0
MINUIT_FIN = 24


def decouper(debut: float, fin: float) -> list[tuple[float, float]]:
    """
    Découpe un créneau quotidien en morceaux qui ne passent pas minuit.

    :param debut: l'heure de début du créneau
    :param fin: l'heure de fin du créneau, le lendemain si elle est plus petite que le début
    :return: les morceaux (début, fin) d'une journée, du plus tôt au plus tard
    """
    if debut <= fin:
        morceaux = [(debut, fin)]
    else:
        morceaux = [(MINUIT_DEBUT, fin), (debut, MINUIT_FIN)]
    return [(debut_morceau, fin_morceau) for debut_morceau, fin_morceau in morceaux
            if debut_morceau < fin_morceau]
