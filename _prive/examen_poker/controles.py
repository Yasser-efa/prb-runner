"""Controls of the poker exam: the layout of the game is free."""


def resume_partie(outcome, case):
    """Keep the hands and the result, whatever the rest of the display."""
    lines = [line.strip() for line in outcome.output.splitlines() if line.strip()]
    computer = [line for line in lines if line.startswith("Tirage ordinateur")]
    start = [rank for rank, line in enumerate(lines) if line.startswith("Tirage joueur")]
    if len(computer) != 1 or len(start) != 1:
        return "« Tirage ordinateur » et « Tirage joueur » doivent apparaitre une seule fois"
    return "\n".join([computer[0], *lines[start[0] :]])
