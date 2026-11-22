"""Programme qui traduit un entier en hexadécimal."""

from conversion import entier_vers_hexa


def main() -> None:
    """
    Demande un entier et affiche son écriture hexadécimale.
    """
    valeur = int(input("Nombre entier ? "))
    print(f"En hexadécimal : {entier_vers_hexa(valeur)}")


if __name__ == "__main__":
    main()
