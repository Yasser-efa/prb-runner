"""Programme qui cherche les moments où Alice et Bob peuvent se voir."""

from agenda.creneaux import creneaux_communs, temps_ensemble
from agenda.saisie import lire_creneaux


def decrire_creneaux(creneaux: list[tuple[int, int]]) -> str:
    """
    Écrit des créneaux sous la forme « début-fin ».

    :param creneaux: les créneaux à écrire
    :return: les créneaux séparés par une espace, ou « aucun » s'il n'y en a pas
    """
    if not creneaux:
        return "aucun"
    return " ".join([f"{debut}-{fin}" for debut, fin in creneaux])


def main() -> None:
    """
    Demande les disponibilités d'Alice et de Bob, puis affiche leurs créneaux communs.
    """
    dispos_alice = lire_creneaux(input("Créneaux d'Alice ? "))
    dispos_bob = lire_creneaux(input("Créneaux de Bob ? "))
    communs = creneaux_communs(dispos_alice, dispos_bob)
    print(f"Créneaux communs : {decrire_creneaux(communs)}")
    print(f"Temps ensemble : {temps_ensemble(dispos_alice, dispos_bob)} h")


if __name__ == "__main__":
    main()
