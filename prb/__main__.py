"""Entry point of ``python -m prb``."""

import sys

try:
    from prb.cli import main
except ModuleNotFoundError as error:
    if error.name not in ("rich", "ruff"):
        raise
    sys.exit(
        f"Il manque « {error.name} ». Choisis l'interpréteur .venv du projet, ou lance : "
        "python -m pip install -r requirements.txt"
    )

sys.exit(main())
