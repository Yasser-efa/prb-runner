"""Compression d'une chaine dans laquelle les nombres égaux à 1 sont omis."""


def decompresser(compresse: str) -> str:
    """
    Retrouve la chaine de départ d'une chaine compressée.

    :param compresse: des caractères suivis de leur nombre de répétitions, omis s'il vaut 1
    :return: la chaine dans laquelle chaque caractère est répété
    """
    resultat = ""
    position = 0
    while position < len(compresse):
        debut_nombre = position + 1
        fin_nombre = debut_nombre
        while fin_nombre < len(compresse) and compresse[fin_nombre].isdigit():
            fin_nombre += 1
        repetitions = 1
        if fin_nombre > debut_nombre:
            repetitions = int(compresse[debut_nombre:fin_nombre])
        resultat += compresse[position] * repetitions
        position = fin_nombre
    return resultat


def ecrire_serie(caractere: str, nombre: int) -> str:
    """
    Écrit une série sous sa forme compressée.

    :param caractere: le caractère répété
    :param nombre: le nombre de répétitions
    :return: le caractère, suivi du nombre s'il dépasse 1
    """
    if nombre > 1:
        return f"{caractere}{nombre}"
    return caractere


def compresser(chaine: str) -> str:
    """
    Compresse une chaine sans écrire les nombres égaux à 1.

    :param chaine: la chaine à compresser
    :return: la chaine compressée
    """
    if not chaine:
        return ""
    resultat = ""
    precedent = chaine[0]
    compteur = 1
    for caractere in chaine[1:]:
        if caractere == precedent:
            compteur += 1
        else:
            resultat += ecrire_serie(precedent, compteur)
            precedent = caractere
            compteur = 1
    return resultat + ecrire_serie(precedent, compteur)
