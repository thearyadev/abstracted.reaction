import pytest
from util.database.database import Database
import docker
from uuid import uuid4
from pathlib import Path
from util.models.film import Film, FilmState, FilmNoBytes
from datetime import datetime, date, timedelta
import copy


@pytest.fixture(scope="module")
def mock_db() -> Database:
    """Uses the Docker SDK to spin up a Postgres15.3 container with some preset configs for testing."""
    docker_client = docker.from_env()
    container = docker_client.containers.create(
        image="postgres:15.3-alpine",
        name=f"abstract.reaction-pytest-postgresql-{uuid4().hex[:8]}",
        ports={"5432/tcp": 5298},
        environment={
            "POSTGRES_USER": "ar-test-user",
            "POSTGRES_PASSWORD": "ar-test-password",
            "POSTGRES_DB": "ar-test-db",
        },
    )
    container.start()
    yield Database(
        db_name="ar-test-db",
        db_user="ar-test-user",
        db_password="ar-test-password",
        db_host="localhost",
        db_port="5298",
        min_connections=5,
        max_connections=15,
        max_retries=15,
        retry_interval=15,
    )
    container.kill()
    container.remove()


def test_database_initializer(mock_db: Database) -> None:
    mock_db.database_init(schema=Path("./util/database/schema.sql").read_text())
    with mock_db.pool.connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT table_name FROM information_schema.tables where table_schema = 'public'"
        )
        result = cur.fetchall()
        assert ("film",) in result
        assert ("rating",) in result
        assert ("history",) in result


def test_none_latest_stamp(mock_db: Database) -> None:
    latest_commit_uuid = mock_db.get_latest_commit_uuid()
    assert latest_commit_uuid is None


def test_get_all_films_empty_list(mock_db: Database) -> None:
    assert not len(mock_db.get_all_films())


def test_get_single_film_doesnt_exist(mock_db: Database) -> None:
    assert mock_db.get_single_film(uuid=uuid4()) is None


def test_get_thumbnail_doesnt_exist(mock_db: Database) -> None:
    assert mock_db.get_thumbnail(uuid4()) is None


def test_get_poster_doesnt_exist(mock_db: Database) -> None:
    assert mock_db.get_poster(uuid4()) is None


def test_insert_film_and_single_pull(mock_db: Database) -> None:
    added_film_uuid = mock_db.insert_film(
        inserted_film := Film(
            uuid=None,
            title="new_film_title",
            date_added=datetime.now(),
            filename="new_filename",
            watched=True,
            state=FilmState.COMPLETE,
            rating=None,
            actresses=["one", "two"],
            thumbnail=b"thumbnail",
            poster=b"poster",
        )
    )

    assert added_film_uuid
    pulled_film: FilmNoBytes = mock_db.get_single_film(added_film_uuid)
    assert isinstance(pulled_film.date_added, date)
    assert isinstance(pulled_film.actresses, list)
    assert isinstance(pulled_film.state, FilmState)
    assert isinstance(pulled_film.watched, bool)
    assert pulled_film.title == inserted_film.title
    assert pulled_film.date_added == inserted_film.date_added.date()
    assert pulled_film.filename == inserted_film.filename
    assert pulled_film.watched == inserted_film.watched
    assert pulled_film.actresses == inserted_film.actresses


def test_valid_latest_commit_uuid(mock_db: Database) -> None:
    assert mock_db.get_latest_commit_uuid()


def test_inserted_film_thumbnail_pull(mock_db: Database) -> None:
    film = mock_db.get_all_films()[0]
    assert isinstance(mock_db.get_thumbnail(film.uuid), bytes)


def test_inserted_film_poster_pull(mock_db: Database) -> None:
    film = mock_db.get_all_films()[0]
    assert isinstance(mock_db.get_poster(film.uuid), bytes)


def test_update_film(mock_db: Database) -> None:
    film = mock_db.get_all_films()[0]
    film.title = new_title = "update_test_title"
    film.actresses = new_actresses = ["update_test_actress", "update_test_actress_2"]
    film.watched = new_watched = not film.watched
    film.state = new_state = FilmState.TRANSCODING
    film.date_added = new_date_added = film.date_added - timedelta(days=10)

    mock_db.update_film(film)
    updated_film = mock_db.get_single_film(uuid=film.uuid)
    assert updated_film.uuid == film.uuid
    assert updated_film.title == new_title
    assert updated_film.actresses == new_actresses
    assert updated_film.watched == new_watched
    assert updated_film.state == new_state
    assert updated_film.date_added == new_date_added


def test_update_film_doesnt_exist(mock_db: Database) -> None:
    film = mock_db.get_all_films()[0]
    film.uuid = uuid4()
    with pytest.raises(ValueError):
        mock_db.update_film(film)


def test_update_rating(mock_db: Database) -> None:
    film = mock_db.get_all_films()[0]

    rating_old = copy.copy(film.rating)
    rating_to_be_updated = copy.copy(film.rating)

    rating_to_be_updated.face = 9
    rating_to_be_updated.pussy = 9
    rating_to_be_updated.boobs = 9
    rating_to_be_updated.positions = 9
    rating_to_be_updated.rearview = 9
    rating_to_be_updated.shots = 9
    rating_to_be_updated.story = 9

    mock_db.update_rating(rating_to_be_updated)
    new_rating = mock_db.get_single_film(film.uuid).rating
    assert new_rating.face == rating_to_be_updated.face
    assert new_rating.pussy == rating_to_be_updated.pussy
    assert new_rating.boobs == rating_to_be_updated.boobs
    assert new_rating.positions == rating_to_be_updated.positions
    assert new_rating.rearview == rating_to_be_updated.rearview
    assert new_rating.shots == rating_to_be_updated.shots
    assert new_rating.story == rating_to_be_updated.story
    assert new_rating.average != rating_old.average  # check if average calc works.


def test_update_rating_doesnt_exist(mock_db: Database):
    rating = mock_db.get_all_films()[0].rating
    rating.uuid = uuid4()
    with pytest.raises(ValueError):
        mock_db.update_rating(rating)
