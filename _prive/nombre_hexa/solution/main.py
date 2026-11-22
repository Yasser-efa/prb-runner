"""Programme qui traduit un nombre hexadécimal."""

from hexa.nombres import valeur_nombre


def main() -> None:
    """
    Demande un nombre hexadécimal et affiche sa valeur.
    """
    nombre = input("Nombre hexadécimal ? ").strip()
    print(f"Valeur : {valeur_nombre(nombre)}")


if __name__ == "__main__":
    main()
