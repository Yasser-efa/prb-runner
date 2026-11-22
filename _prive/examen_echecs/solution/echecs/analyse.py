"""Chargement, dessin et analyse d'un échiquier."""

from echecs import deplacements, pieces

TAILLE = 8
PIECE, COULEUR = "piece", "couleur"
ROI = "ROI"
CASE_VIDE = {PIECE: "CASE_VIDE", COULEUR: pieces.BLANC}


def charger_depuis(chemin: str) -> dict[tuple[int, int], dict[str, str]]:
    """
    Charge un échiquier depuis un fichier.

    :param chemin: le chemin du fichier
    :return: l'échiquier, vide si le fichier ne peut pas être lu
    """
    echiquier = {}
    try:
        with open(chemin, encoding="utf-8") as fichier:
            for texte in fichier:
                piece, couleur, ligne, colonne = texte.split()
                echiquier[int(ligne), int(colonne)] = {PIECE: piece, COULEUR: couleur}
    except OSError:
        return {}
    return echiquier


def dessiner(echiquier: dict[tuple[int, int], dict[str, str]]) -> None:
    """
    Affiche un échiquier.

    :param echiquier: les pièces placées sur l'échiquier
    """
    for ligne in range(TAILLE):
        for colonne in range(TAILLE):
            contenu = echiquier.get((ligne, colonne), CASE_VIDE)
            couleur_case = pieces.NOIR
            if (ligne + colonne) % 2 == 0:
                couleur_case = pieces.BLANC
            pieces.afficher(contenu[PIECE], contenu[COULEUR], couleur_case)
        print()


def est_dans_echiquier(position: tuple[int, int]) -> bool:
    """
    Vérifie si une position existe.

    :param position: la position à vérifier
    :return: vrai si la position est dans l'échiquier
    """
    ligne, colonne = position
    return 0 <= ligne < TAILLE and 0 <= colonne < TAILLE


def cases_attaquees(
    echiquier: dict[tuple[int, int], dict[str, str]], position: tuple[int, int]
) -> set[tuple[int, int]]:
    """
    Cherche les cases attaquées par une pièce.

    :param echiquier: les pièces placées sur l'échiquier
    :param position: la position de la pièce
    :return: les cases où la pièce peut se déplacer ou capturer
    """
    piece, couleur = echiquier[position][PIECE], echiquier[position][COULEUR]
    distance = deplacements.NB_MAX_DEPLACEMENTS[piece]
    attaquees = set()
    for direction in deplacements.DIRECTIONS_DEPLACEMENTS[piece]:
        trajet = deplacements.calculer_en_theorie(position, direction, distance)
        pas = 0
        while pas < distance and est_dans_echiquier(trajet[pas]) and trajet[pas] not in echiquier:
            attaquees.add(trajet[pas])
            pas += 1
        if pas < distance and trajet[pas] in echiquier:
            if echiquier[trajet[pas]][COULEUR] != couleur:
                attaquees.add(trajet[pas])
    return attaquees


def positions_roi_blanc(
    echiquier: dict[tuple[int, int], dict[str, str]]
) -> list[tuple[int, int]]:
    """
    Cherche le roi blanc.

    :param echiquier: les pièces placées sur l'échiquier
    :return: une liste avec la position du roi, vide s'il n'y en a pas
    """
    return [position for position, contenu in echiquier.items()
            if contenu == {PIECE: ROI, COULEUR: pieces.BLANC}]


def roi_blanc_en_echec(echiquier: dict[tuple[int, int], dict[str, str]]) -> bool:
    """
    Vérifie si le roi blanc est en échec.

    :param echiquier: les pièces placées sur l'échiquier
    :return: vrai si une pièce noire attaque le roi blanc
    """
    attaquees = set()
    for position, contenu in echiquier.items():
        if contenu[COULEUR] == pieces.NOIR:
            attaquees |= cases_attaquees(echiquier, position)
    return any([position in attaquees for position in positions_roi_blanc(echiquier)])


def roi_blanc_en_mat(echiquier: dict[tuple[int, int], dict[str, str]]) -> bool:
    """
    Vérifie si le roi blanc est échec et mat.

    :param echiquier: les pièces placées sur l'échiquier
    :return: vrai si le roi est en échec et le reste où qu'il aille
    """
    if not roi_blanc_en_echec(echiquier):
        return False
    depart = positions_roi_blanc(echiquier)[0]
    for arrivee in cases_attaquees(echiquier, depart):
        deplace = echiquier.copy()
        deplace[arrivee] = deplace.pop(depart)
        if not roi_blanc_en_echec(deplace):
            return False
    return True
