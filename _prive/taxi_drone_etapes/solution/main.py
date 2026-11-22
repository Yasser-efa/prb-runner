"""Programme qui calcule la longueur d'un trajet en taxi."""

from trajets import distance_trajet, lire_etapes


def main() -> None:
    """
    Demande les étapes d'un trajet et affiche sa longueur.
    """
    etapes = lire_etapes(input("Étapes ? "))
    print(f"Distance : {distance_trajet(etapes)}")


if __name__ == "__main__":
    main()
