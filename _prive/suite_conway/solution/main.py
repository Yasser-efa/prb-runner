"""Programme qui affiche les premiers termes de la suite de Conway."""

from suite_de_conway import serie


def main() -> None:
    """
    Demande un nombre de termes et les affiche, un par ligne.
    """
    nb_termes = int(input("Nombre de termes ? "))
    for terme in serie(nb_termes):
        print(terme)


if __name__ == "__main__":
    main()
