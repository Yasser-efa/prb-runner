def decompresser(compresse: str) -> str:
    """
    Decompresse un str
    :param compresse: version compressée
    :return: version décompressée
    """
    return "".join(compresse[i] * int(compresse[i + 1]) for i in range(0, len(compresse), 2))


def taille_decompressee(compresse: str) -> int:
    """
    renvoie la longueur de la version décompressée sans la décompresser
    :param compresse: str compressée
    :return: longueur de la version décompressée
    """
    return len("".join(compresse[i] * int(compresse[i + 1]) for i in range(0, len(compresse), 2)))
