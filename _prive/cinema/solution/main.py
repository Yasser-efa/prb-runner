"""Programme qui indique où se trouve un siège."""

from salle.sieges import position_siege

NB_SIEGES = 240


def main() -> None:
    """
    Demande un numéro de siège et affiche sa rangée et sa position.
    """
    siege = int(input("Numéro du siège ? "))
    if 1 <= siege <= NB_SIEGES:
        rangee, position = position_siege(siege)
        print(f"Rangée {rangee}, position {position}")
    else:
        print("Ce siège n'existe pas.")


if __name__ == "__main__":
    main()
