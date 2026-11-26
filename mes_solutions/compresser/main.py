import compresseur


def main():
    """
    Fonction principale
    :return: rien
    """
    chaine = input("Chaine ? ")
    print(f"Compressée : {compresseur.compresser(chaine)}")
    print(f"Longueur : {len(chaine)} -> {len(compresseur.compresser(chaine))}")


if __name__ == "__main__":
    main()
