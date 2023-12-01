import logging
import os
import shutil
import time
from pathlib import Path

import ffmpeg

from util.database.database import Database
from util.models.film import FilmState


def ensure_io_permissions(path: Path) -> bool:
    return all((os.access(path, os.R_OK), os.access(path, os.W_OK),))


def encode(input_file: Path, output_file: Path) -> None:
    ...


def delete(file: Path) -> None:
    assert file.exists()
    assert file.is_file()
    assert not file.is_dir()
    shutil.rmtree(path=file)


def rename(target: Path, destination: Path) -> None:
    assert target.exists()
    assert target.is_file()
    assert destination.is_file()
    target.rename(destination)


def main() -> int:
    db = Database.from_env(load_dot_env=True)
    db.database_init(Path("../util/database/schema.sql").read_text())

    sleep_time = int(os.environ["TRANSCODER_SLEEP_TIME"])
    media_path = Path(os.environ["APP_FILM_PATH"])

    while True:
        if (film := db.get_not_transcoded_and_set_transcoding()) is None:
            logging.info(
                f"No films waiting for transcode. Waiting {sleep_time} seconds."
            )
            time.sleep(sleep_time)
            continue
        film_file_path = media_path / film.filename
        transcoded_file_path = media_path / f"{film.filename}.artranscode"
        encode(
            input_file=film_file_path,
            output_file=transcoded_file_path,
        )

        delete(file=film_file_path)
        rename(target=transcoded_file_path, destination=film_file_path)
        updated_film = db.get_single_film(film.uuid)  # fetch again to ensure data is the most up to date.
        updated_film.state = FilmState.COMPLETE
        db.update_film(updated_film)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
