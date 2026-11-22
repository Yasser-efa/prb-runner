"""Programme qui analyse un échiquier."""

from echecs.analyse import charger_depuis, dessiner, roi_blanc_en_echec, roi_blanc_en_mat


def main() -> None:
    """
    Demande un fichier, affiche son échiquier et indique si le roi blanc est en échec.
    """
    print("-- Analyse d'échiquier --")
    echiquier = charger_depuis(input("Chemin du fichier ? "))
    dessiner(echiquier)
    if roi_blanc_en_mat(echiquier):
        print("Échec\n ... et Mat !")
    elif roi_blanc_en_echec(echiquier):
        print("Échec !")
    else:
        print("Pas d'échec.")


if __name__ == "__main__":
    main()
