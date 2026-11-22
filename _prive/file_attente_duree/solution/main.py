"""Programme qui calcule la durée nécessaire pour atteindre un effectif."""

from attente import minutes_necessaires


def main() -> None:
    """
    Demande l'effectif de départ et l'effectif voulu, puis affiche la durée.
    """
    depart = int(input("Effectif de départ ? "))
    voulu = int(input("Effectif voulu ? "))
    print(f"Durée : {minutes_necessaires(depart, voulu)} min")


if __name__ == "__main__":
    main()
