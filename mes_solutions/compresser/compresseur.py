def obtenir_couples(chaine: str) -> list[tuple[str, int]]:
    """
    À partir d'un string décompressé, obtenir les couples
    :param chaine: string décompressé
    :return: couples
    """
    output = []
    if not chaine:
        return output
    debut = chaine[0]
    nbr = 1
    for iteration in range(1, len(chaine)):
        if debut == chaine[iteration]:
            nbr += 1
        else:
            output.append((debut, nbr))
            debut = chaine[iteration]
            nbr = 1
    output.append((chaine[-1], nbr))
    return output


def compresser(chaine: str) -> str:
    """
    Compresse les couples en string
    :param chaine: chaine décompressée
    :return: chaine compressée
    """
    output = ""
    if not chaine:
        return output
    couples = obtenir_couples(chaine)
    for couple in couples:
        output += couple[0] + str(couple[1])
    return output
