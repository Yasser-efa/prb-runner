"""Programme qui retrouve l'effectif de départ d'une file d'attente."""

from attente import effectif_depart


def main() -> None:
    """
    Demande l'effectif final et la durée, puis affiche l'effectif de départ.
    """
    effectif_final = int(input("Effectif final ? "))
    minutes = int(input("Nombre de minutes ? "))
    depart = effectif_depart(effectif_final, minutes)
    if depart < 0:
        print("Situation impossible.")
    else:
        print(f"Effectif de départ : {depart}")


if __name__ == "__main__":
    main()
