"""The student's folders: creation, provided files and archiving."""

from datetime import datetime
from pathlib import Path

from prb.model import Exercise
from prb.paths import Paths
from prb.sources import list_files


class WorkspaceError(Exception):
    """A file of the student could not be moved."""


def prepare_folder(paths: Paths, exercise: Exercise, restore: bool = False) -> Path:
    """Create the folder of an exercise and copy the provided files.

    :param paths: the project folders
    :param exercise: the exercise
    :param restore: copy the missing files even if the student has already started
    :return: the folder
    """
    folder = paths.solutions / exercise.id
    folder.mkdir(parents=True, exist_ok=True)
    if restore or not list_files(folder):
        present = set(list_files(folder))
        for file in exercise.provided:
            if file.name not in present:
                target = folder / file.name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(file.read())
    return folder


def own_files(folder: Path, exercise: Exercise) -> list[str]:
    """List the files written by the student.

    :param folder: the student's folder
    :param exercise: the exercise
    :return: the files that were not provided
    """
    return [name for name in list_files(folder) if name not in exercise.provided_names]


def archive_folder(paths: Paths, exercise: Exercise, at: datetime) -> Path | None:
    """Put the previous code aside, so that a review starts from an empty folder.

    Everything is moved, nothing is deleted.

    :param paths: the project folders
    :param exercise: the exercise
    :param at: current time, used as the name of the archive
    :return: the archive, None if there was nothing to put aside
    """
    folder = paths.solutions / exercise.id
    if not own_files(folder, exercise):
        return None
    archive = paths.archives / exercise.id / f"{at:%Y-%m-%d_%Hh%Mm%S}"
    archive.mkdir(parents=True, exist_ok=True)
    for child in list(folder.iterdir()):
        try:
            child.rename(archive / child.name)
        except OSError as error:
            raise WorkspaceError(
                f"impossible de ranger mes_solutions/{exercise.id}/{child.name} "
                f"({error.strerror}). Ferme ce qui l'utilise, puis relance."
            ) from error
    return archive
