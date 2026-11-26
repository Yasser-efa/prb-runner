# Hypothèses
#
#  • Une heure est un nombre entre 0 et 24, éventuellement décimal : 14.5 représente 14 h 30.
#  • Un créneau commence et se termine le même jour. On considère que son début ne dépasse jamais sa fin.
#  • Les durées sont exprimées en heures.

# Mots clés interdits: break, continue, try et while True
def temps_ensemble(debut_alice: int, fin_alice: int, debut_bob: int, fin_bob: int):
    """
    Cette fonction prend en argument les heures de début et de fin du créneau d'Alice,
    puis de celui de Bob pour retourner le temps qu'ils peuvent passer ensemble.
    S'ils ne peuvent pas se voir, elle renvoie 0.
    :param debut_alice: heure début Alice
    :type debut_alice: int
    :param fin_alice: Heure fin Alice
    :type fin_alice: int
    :param debut_bob: Heure début Bob
    :type debut_bob: int
    :param fin_bob: Heure fin Bob
    :type fin_bob: int
    :return: Elle renvoie le temps qu'ils peuvent passer ensemble en heure.
    :rtype: int
    """
    # Alice commence son créneau avant Bob
    if debut_alice < debut_bob:
        # Vérifier s'il y a un créneau commun
        if fin_alice < debut_bob:
            return 0
        # Le creneau de bob est à l'intérieur ou à l'extérieur du créneau de Alice ?
        elif fin_bob < fin_alice:
            return fin_bob - debut_bob
        # Le creneau de bob commence et finit après celui de Alice
        else:
            return fin_alice - debut_bob
    # Bob commence son créneau avant Alice
    elif debut_alice > debut_bob:
        # Vérifier s'il y a un créneau commun
        if fin_bob < debut_alice:
            return 0
        elif fin_alice < fin_bob:
            # Le creneau de Alice est à l'intérieur ou à l'extérieur du créneau de Bob ?
            return fin_alice - debut_alice
        # Le creneau de bob commence et finit après celui de Alice
        else:
            return fin_bob - debut_alice
    # Bob et Alice commence leur créneau en même temps
    else:
        # Alice finit avant Bob
        if fin_alice < fin_bob:
            return fin_alice - debut_alice
        # Alice finit après Bob
        elif fin_alice > fin_bob:
            return fin_bob - debut_bob
        # Ils finissent en même temps
        else:
            return fin_bob - debut_bob


def temps_groupe(creneaux: tuple[int, int]):
    """
    Cette fonction prend en argument une liste de créneaux, un par personne. Chaque
    créneau est un tuple (debut, fin). Elle renvoie le temps que toutes les
    personnes peuvent passer ensemble. Si la liste est vide, elle renvoie 0. La
    liste reçue ne doit pas être modifiée.
    :param creneaux: liste de créneaux
    :type creneaux: tuple[int, int]
    :return: le temps que toutes les personnes peuvent passer ensemble
    :rtype: int
    """
    if not creneaux:
        return 0
    debut = [creneau[0] for creneau in creneaux]
    fin = [creneau[1] for creneau in creneaux]
    return min(fin) - max(debut) if min(fin) - max(debut) >= 0 else 0


# Exemples:
#  >>> temps_ensemble(14, 17, 15, 19)
#  2
#  >>> temps_ensemble(9, 12, 14, 18)
#  0
#  >>> temps_ensemble(10, 18, 12.5, 13.5)
#  1.0
# Alice commence avant bob
# Alice finit avant bob

if __name__ == "__main__":
    print(temps_ensemble(14, 17, 15, 19))
