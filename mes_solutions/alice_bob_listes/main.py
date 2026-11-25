from agenda.saisie import lire_creneaux
from agenda.creneaux import creneaux_communs, temps_ensemble


def main():
    """
    Demande les créneaux d'Alice et de Bob, puis affiche leurs créneaux communs
    et le temps total qu'ils peuvent passer ensemble.
    """
    dispos_alice = lire_creneaux(input("Créneaux d'Alice ? "))
    dispos_bob = lire_creneaux(input("Créneaux de Bob ? "))

    communs = creneaux_communs(dispos_alice, dispos_bob)
    if communs:
        textes = [f"{debut}-{fin}" for debut, fin in communs]
        affichage = " ".join(textes)
    else:
        affichage = "aucun"

    print(f"Créneaux communs : {affichage}")
    print(f"Temps ensemble : {temps_ensemble(dispos_alice, dispos_bob)} h")


if __name__ == "__main__":
    main()
