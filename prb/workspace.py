"""The student's folders: creation and archiving."""

from datetime import datetime
from pathlib import Path

from prb.paths import Paths
from prb.sources import list_files


class WorkspaceError(Exception):
    """A file of the student could not be moved."""


def prepare_folder(paths: Paths, exercise_id: str) -> Path:
    """Create the folder of an exercise if needed.

    :param paths: the project folders
    :param exercise_id: the exercise
    :return: the folder
    """
    folder = paths.solutions / exercise_id
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def archive_folder(paths: Paths, exercise_id: str, at: datetime) -> Path | None:
    """Put the previous code aside, so that a review starts from an empty folder.

    Everything is moved, nothing is deleted.

    :param paths: the project folders
    :param exercise_id: the exercise
    :param at: current time, used as the name of the archive
    :return: the archive, None if there was nothing to put aside
    """
    folder = prepare_folder(paths, exercise_id)
    if not list_files(folder):
        return None
    archive = paths.archives / exercise_id / f"{at:%Y-%m-%d_%Hh%Mm%S}"
    archive.mkdir(parents=True, exist_ok=True)
    for child in list(folder.iterdir()):
        try:
            child.rename(archive / child.name)
        except OSError as error:
            raise WorkspaceError(
                f"impossible de ranger mes_solutions/{exercise_id}/{child.name} "
                f"({error.strerror}). Ferme ce qui l'utilise, puis relance."
            ) from error
    return archive
