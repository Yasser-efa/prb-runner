"""Programme qui compresse une chaine tapée par l'utilisateur."""

from compresseur import compresser


def main() -> None:
    """
    Demande une chaine et affiche sa version compressée.
    """
    chaine = input("Chaine ? ")
    compressee = compresser(chaine)
    print(f"Compressée : {compressee}")
    print(f"Longueur : {len(chaine)} -> {len(compressee)}")


if __name__ == "__main__":
    main()
