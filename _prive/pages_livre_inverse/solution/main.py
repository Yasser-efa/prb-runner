"""Programme qui retrouve le nombre de pages d'un livre."""

from numerotation import nombre_pages


def main() -> None:
    """
    Demande un nombre de chiffres et affiche le nombre de pages du livre.
    """
    pages = nombre_pages(int(input("Nombre de chiffres ? ")))
    if pages < 0:
        print("Aucun livre ne convient.")
    else:
        print(f"Nombre de pages : {pages}")


if __name__ == "__main__":
    main()
