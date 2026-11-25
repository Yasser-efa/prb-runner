def lire_creneaux(texte: str) -> list[tuple[int, int]]:
    """
    Renvoie une liste des différents créneaux à partir d'un texte de la forme "debut-fin debut-fin..."
    :param texte: texte sous forme de plusieurs "debut-fin" séparés par un ou plusieurs espaces
    :return: liste de créneaux sous forme [(9, 12), (14, 17)]
    """
    templist = texte.split()
    output = []
    for creneau in templist:
        creneautemp = creneau.split("-")
        n1 = int(creneautemp[0])
        n2 = int(creneautemp[1])
        output.append((n1, n2))
    return output
