"""Programme qui cherche un jour de la semaine."""

from calendrier import jour_apres


def main() -> None:
    """
    Demande un jour et un nombre de jours, puis affiche le jour obtenu.
    """
    jour = input("Jour de départ ? ").strip().lower()
    nb_jours = int(input("Nombre de jours ? "))
    print(f"Résultat : {jour_apres(jour, nb_jours)}")


if __name__ == "__main__":
    main()
