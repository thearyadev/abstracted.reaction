import copy
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Generator
from uuid import uuid4

import docker
import pytest

from util.database.database import Database
from util.models.actress_detail import ActressDetail
from util.models.film import Film, FilmNoBytes, FilmState


@pytest.fixture(scope="module")
def mock_db() -> Generator[Database, None, None]:
    """Uses the Docker SDK to spin up a Postgres15.3 container with some preset configs for testing."""
    docker_client: docker.client.DockerClient = docker.from_env()
    for existing_container in docker_client.containers.list():
        if existing_container.name.startswith("abstract.reaction-pytest-postgresql-"):
            existing_container.kill()  # pragma: no cover
            existing_container.remove()  # pragma: no cover

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


@pytest.mark.order(100)
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


@pytest.mark.order(101)
def test_none_latest_stamp(mock_db: Database) -> None:
    latest_commit_uuid = mock_db.get_latest_commit_uuid()
    assert latest_commit_uuid is None


@pytest.mark.order(101)
def test_get_not_transcoded_and_set_transcoding_no_records(mock_db: Database) -> None:
    result = mock_db.get_not_transcoded_and_set_transcoding()
    assert result is None


@pytest.mark.order(102)
def test_get_all_films_empty_list(mock_db: Database) -> None:
    assert not len(mock_db.get_all_films())


@pytest.mark.order(103)
def test_get_single_film_doesnt_exist(mock_db: Database) -> None:
    assert mock_db.get_single_film(uuid=uuid4()) is None


@pytest.mark.order(104)
def test_get_thumbnail_doesnt_exist(mock_db: Database) -> None:
    assert mock_db.get_thumbnail(uuid4()) is None


@pytest.mark.order(105)
def test_get_poster_doesnt_exist(mock_db: Database) -> None:
    assert mock_db.get_poster(uuid4()) is None


@pytest.mark.order(106)
def test_actress_list_no_results(mock_db: Database) -> None:
    actresses = mock_db.get_actress_list()
    assert not len(actresses)


@pytest.mark.order(106)
def test_actress_detail_no_results(mock_db: Database) -> None:
    result = mock_db.get_actress_detail(name="no exist")
    assert isinstance(result, ActressDetail)
    assert isinstance(result.name, str)
    assert isinstance(result.films, list)
    assert len(result.name)
    assert not len(result.films)


@pytest.mark.order(107)
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
    pulled_film = mock_db.get_single_film(added_film_uuid)
    assert isinstance(pulled_film, FilmNoBytes)
    assert isinstance(pulled_film.date_added, date)
    assert isinstance(pulled_film.actresses, list)
    assert isinstance(pulled_film.state, FilmState)
    assert isinstance(pulled_film.watched, bool)
    assert pulled_film.title == inserted_film.title
    assert pulled_film.date_added == inserted_film.date_added.date()
    assert pulled_film.filename == inserted_film.filename
    assert pulled_film.watched == inserted_film.watched
    assert pulled_film.actresses == inserted_film.actresses


@pytest.mark.order(108)
def test_valid_latest_commit_uuid(mock_db: Database) -> None:
    assert mock_db.get_latest_commit_uuid()


@pytest.mark.order(109)
def test_inserted_film_thumbnail_pull(mock_db: Database) -> None:
    film = mock_db.get_all_films()[0]
    assert film.uuid
    assert isinstance(mock_db.get_thumbnail(film.uuid), bytes)


@pytest.mark.order(110)
def test_inserted_film_poster_pull(mock_db: Database) -> None:
    film = mock_db.get_all_films()[0]
    assert film.uuid
    assert isinstance(mock_db.get_poster(film.uuid), bytes)


@pytest.mark.order(111)
def test_update_film(mock_db: Database) -> None:
    film = mock_db.get_all_films()[0]
    film.title = new_title = "update_test_title"
    film.actresses = new_actresses = ["update_test_actress", "update_test_actress_2"]
    film.watched = new_watched = not film.watched
    film.state = new_state = FilmState.TRANSCODING
    film.date_added = new_date_added = film.date_added - timedelta(days=10)

    mock_db.update_film(film)
    assert film.uuid
    updated_film = mock_db.get_single_film(uuid=film.uuid)
    assert updated_film
    assert updated_film.uuid == film.uuid
    assert updated_film.title == new_title
    assert updated_film.actresses == new_actresses
    assert updated_film.watched == new_watched
    assert updated_film.state == new_state
    assert updated_film.date_added == new_date_added


@pytest.mark.order(112)
def test_update_film_doesnt_exist(mock_db: Database) -> None:
    film = mock_db.get_all_films()[0]
    assert film
    film.uuid = uuid4()
    with pytest.raises(ValueError):
        mock_db.update_film(film)


@pytest.mark.order(113)
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
    assert film.uuid
    new_film = mock_db.get_single_film(film.uuid)
    assert new_film
    new_rating = new_film.rating
    assert new_rating.face == rating_to_be_updated.face
    assert new_rating.pussy == rating_to_be_updated.pussy
    assert new_rating.boobs == rating_to_be_updated.boobs
    assert new_rating.positions == rating_to_be_updated.positions
    assert new_rating.rearview == rating_to_be_updated.rearview
    assert new_rating.shots == rating_to_be_updated.shots
    assert new_rating.story == rating_to_be_updated.story
    assert new_rating.average != rating_old.average  # check if average calc works.


@pytest.mark.order(114)
def test_update_rating_doesnt_exist(mock_db: Database) -> None:
    rating = mock_db.get_all_films()[0].rating
    rating.uuid = uuid4()
    with pytest.raises(ValueError):
        mock_db.update_rating(rating)


@pytest.mark.order(115)
def test_actress_list(mock_db: Database) -> None:
    actresses = mock_db.get_actress_list()
    assert isinstance(actresses, list)
    assert isinstance(actresses[0], str)


@pytest.mark.order(116)
def test_film_delete_doesnt_exist(mock_db: Database) -> None:
    mock_db.delete_film(uuid4())


@pytest.mark.order(117)
def test_film_delete(mock_db: Database) -> None:
    film = mock_db.get_all_films()[0]
    assert film.uuid
    mock_db.delete_film(film.uuid)
    assert mock_db.get_single_film(film.uuid) is None


@pytest.mark.order(118)
def test_actress_detail(mock_db: Database) -> None:
    for i in range(10):
        mock_db.insert_film(
            Film(
                uuid=None,
                title="new_film_title",
                date_added=datetime.now(),
                filename="new_filename",
                watched=True,
                state=FilmState.COMPLETE,
                rating=None,
                actresses=["four", "five"],
                thumbnail=b"thumbnail",
                poster=b"poster",
            )
        )

    for i in range(10):
        mock_db.insert_film(
            Film(
                uuid=None,
                title="new_film_title",
                date_added=datetime.now(),
                filename="new_filename",
                watched=True,
                state=FilmState.COMPLETE,
                rating=None,
                actresses=["three", "five"],
                thumbnail=b"thumbnail",
                poster=b"poster",
            )
        )

    result_two = mock_db.get_actress_detail(name="five")
    result_three = mock_db.get_actress_detail(name="three")
    assert isinstance(result_two, ActressDetail)
    assert isinstance(result_two.name, str)
    assert isinstance(result_two.films, list)
    assert len(result_two.name)
    assert len(result_two.films)
    assert isinstance(result_two.films[0], FilmNoBytes)

    assert len(result_two.films) == 20
    assert len(result_three.films) == 10


@pytest.mark.order(119)
def test_get_not_transcoded_and_set_transcoding(mock_db: Database) -> None:
    films = mock_db.get_all_films()
    selected_films = films[:(count := 5)]
    for i in selected_films:
        i.state = FilmState.NOT_TRANSCODED
        mock_db.update_film(i)
    for i in range(count):
        result_exists = mock_db.get_not_transcoded_and_set_transcoding()
        assert result_exists
        assert result_exists.state == FilmState.TRANSCODING
    assert mock_db.get_not_transcoded_and_set_transcoding() is None
