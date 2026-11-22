"""Programme qui calcule la vitesse moyenne d'un aller-retour."""

from trajets import vitesse_aller_retour


def main() -> None:
    """
    Demande les vitesses d'un aller-retour et affiche la vitesse moyenne.
    """
    vitesse_aller = float(input("Vitesse à l'aller (km/h) ? "))
    vitesse_retour = float(input("Vitesse au retour (km/h) ? "))
    print(f"Vitesse moyenne : {vitesse_aller_retour(vitesse_aller, vitesse_retour):.1f} km/h")


if __name__ == "__main__":
    main()
