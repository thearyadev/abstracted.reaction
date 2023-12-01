import datetime
from dataclasses import asdict
from pathlib import Path
from typing import Any
from uuid import uuid4

import dotenv
import httpx
import pytest
from fastapi.testclient import TestClient

from server.__main__ import Server
from util.database.database import Database
from util.models.film import Film, FilmNoBytes, FilmState

from .database_test import mock_db


@pytest.fixture(scope="module")
def server(mock_db: Database) -> Server:
    dotenv.load_dotenv()
    mock_db.database_init(Path("./util/database/schema.sql").read_text())
    server = Server(
        host="0.0.0.0", port=9761, db=mock_db
    )  # host and port unused in this context.
    return server


@pytest.fixture(scope="module")
def client(server: Server) -> TestClient:
    return server.test_client()


@pytest.mark.order(201)
def test_api_films_empty(client: TestClient) -> None:
    response = client.get("/api/get/films")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert not len(response.json())


@pytest.mark.order(202)
def test_api_film_no_result(client: TestClient) -> None:
    response = client.get(f"/api/get/film?uuid={uuid4()}")
    assert response.status_code == 404
    assert response.json() == {"detail": "film not found"}


@pytest.mark.order(203)
def test_api_image_doesnt_exist(client: TestClient) -> None:
    poster_response = client.get(f"/api/get/image?uuid={uuid4()}&image_type=POSTER")
    thumbnail_response = client.get(
        f"/api/get/image?uuid={uuid4()}&image_type=THUMBNAIL"
    )
    assert poster_response.status_code == 404
    assert poster_response.json() == {"detail": "film not found"}
    assert thumbnail_response.status_code == 404
    assert thumbnail_response.json() == {"detail": "film not found"}


@pytest.mark.order(204)
def test_api_set_rating_doesnt_exist(client: TestClient) -> None:
    response = client.post(
        "/api/set/rating",
        json={
            "rating": {
                "uuid": str(uuid4()),
                "average": 3.1,
                "story": 9,
                "positions": 8,
                "pussy": 10,
                "shots": 3,
                "boobs": 2,
                "face": 9,
                "rearview": 10,
            }
        },
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "rating not found"}


@pytest.mark.order(205)
def test_api_delete_film_doesnt_exist(client: TestClient) -> None:
    response = client.post(
        f"/api/set/delete?uuid={uuid4()}",
    )
    assert response.status_code == 200


@pytest.mark.order(206)
def test_api_set_watch_status_doesent_exist(client: TestClient) -> None:
    response = client.post(f"/api/set/watched?uuid={uuid4()}&watch_status={True}")
    assert response.status_code == 404
    assert response.json() == {"detail": "film not found"}


@pytest.mark.order(207)
def test_api_get_actress_list_no_entries(client: TestClient) -> None:
    response = client.get("/api/get/actresses")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert not len(response.json())


@pytest.mark.order(207)
def test_api_get_serve_video_film_doesnt_exist_by_uuid(client: TestClient) -> None:
    response = client.get(f"/api/get/video?uuid={uuid4()}")
    assert response.status_code == 404
    assert response.json() == {"detail": "film not found"}


@pytest.mark.order(207)
def test_api_get_actress_detail_no_results(client: TestClient) -> None:
    response = client.get("/api/get/actress_detail?name=gnome")
    assert response.status_code == 200
    assert response.json() == {"name": "gnome", "films": []}


@pytest.mark.order(208)
def test_api_films_no_cache(client: TestClient, mock_db: Database) -> None:
    film = Film(
        uuid=None,
        title="new_film_title",
        date_added=datetime.datetime.now(),
        filename="new_filename",
        watched=True,
        state=FilmState.COMPLETE,
        rating=None,
        actresses=["one", "two"],
        thumbnail=b"thumbnail",
        poster=b"poster",
    )
    for i in range(size := 100):
        mock_db.insert_film(film)

    response = client.get("/api/get/films")
    assert response.status_code == 200
    assert isinstance(json := response.json(), list)
    assert len(json) == size


@pytest.mark.order(209)
def test_api_get_serve_video_film_exists_file_not_found(
    client: TestClient, mock_db: Database
) -> None:
    film = mock_db.get_all_films()[0]
    assert film.uuid
    response_uuid_fetch = client.get(f"/api/get/video?uuid={film.uuid}")
    assert response_uuid_fetch.status_code == 501
    assert response_uuid_fetch.json() == {"detail": "file not found"}

    response_filename_fetch = client.get(
        f"/api/get/video?uuid={uuid4()}&filename={film.filename}"
    )
    assert response_filename_fetch.status_code == 501
    assert response_uuid_fetch.json() == {"detail": "file not found"}


@pytest.mark.order(209)
def test_api_get_serve_video_film_exists_file_found(
    client: TestClient, mock_db: Database
) -> None:
    film = mock_db.get_all_films()[0]
    assert film.uuid
    film.filename = "test_video_file.mp4"
    mock_db.update_film(film)
    assert (
        mock_db.get_single_film(film.uuid).filename == film.filename
    )  # Filename update was not successful.
    response_uuid_fetch = client.get(f"/api/get/video?uuid={film.uuid}")
    assert response_uuid_fetch.status_code == 200

    response_filename_fetch = client.get(
        f"/api/get/video?uuid={uuid4()}&filename={film.filename}",
    )
    assert response_filename_fetch.status_code == 200


@pytest.mark.order(209)
def test_api_films_cache(client: TestClient, server: Server) -> None:
    assert server.cache.films


@pytest.mark.order(209)
def test_api_film(client: TestClient, mock_db: Database) -> None:
    film = mock_db.get_all_films()[0]
    assert film.uuid
    response = client.get(f"/api/get/film?uuid={film.uuid}")
    assert response.status_code == 200
    assert response.json()


@pytest.mark.order(210)
def test_api_thumbnail_no_cache(client: TestClient, mock_db: Database) -> None:
    film = mock_db.get_all_films()[0]
    assert film.uuid
    response = client.get(f"/api/get/image?uuid={film.uuid}&image_type=THUMBNAIL")
    assert response.status_code == 200
    assert response.headers.get("Content-Type") == "image/png"
    assert isinstance(response.content, bytes)
    assert response.content.decode("utf-8") == "thumbnail"


@pytest.mark.order(211)
def test_api_thumbnail_cache(
    client: TestClient, mock_db: Database, server: Server
) -> None:
    film = mock_db.get_all_films()[0]
    assert film.uuid
    client.get(f"/api/get/image?uuid={film.uuid}&image_type=THUMBNAIL")
    response = client.get(f"/api/get/image?uuid={film.uuid}&image_type=THUMBNAIL")
    assert response.status_code == 200
    assert response.headers.get("Content-Type") == "image/png"
    assert isinstance(response.content, bytes)
    assert response.content.decode("utf-8") == "thumbnail"
    assert film.uuid in list(server.cache.images.keys())
    assert response.content == server.cache.images[film.uuid]


@pytest.mark.order(212)
def test_api_poster(client: TestClient, mock_db: Database) -> None:
    film = mock_db.get_all_films()[0]
    assert film.uuid
    response = client.get(f"/api/get/image?uuid={film.uuid}&image_type=POSTER")
    assert response.status_code == 200
    assert response.headers.get("Content-Type") == "image/png"
    assert isinstance(response.content, bytes)
    assert response.content.decode("utf-8") == "poster"


@pytest.mark.order(213)
def test_api_set_rating(client: TestClient, mock_db: Database) -> None:
    film = mock_db.get_all_films()[0]
    assert film.uuid
    rating = film.rating
    rating.average = 5
    rating.face = 10
    rating.pussy = 10
    rating.positions = 10
    rating.rearview = 10
    rating.shots = 10
    rating.boobs = 10
    rating.story = 10
    rating.uuid = str(rating.uuid)  # uuid is not json serializable.

    response = client.post("/api/set/rating", json={"rating": asdict(rating)})
    assert response.status_code == 200
    updated_film = mock_db.get_single_film(film.uuid)
    assert updated_film
    assert updated_film.rating.average == 10
    assert updated_film.rating.face == 10
    assert updated_film.rating.pussy == 10
    assert updated_film.rating.positions == 10
    assert updated_film.rating.rearview == 10
    assert updated_film.rating.shots == 10
    assert updated_film.rating.boobs == 10
    assert updated_film.rating.story == 10


@pytest.mark.order(214)
def test_api_delete_film(client: TestClient, mock_db: Database) -> None:
    film = mock_db.get_all_films()[0]
    assert film.uuid
    response = client.post(f"/api/set/delete?uuid={film.uuid}")
    assert response.status_code == 200
    assert film.uuid not in [str(f.uuid) for f in mock_db.get_all_films()]


@pytest.mark.order(215)
def test_api_set_watch_status_exists(client: TestClient, mock_db: Database) -> None:
    film = mock_db.get_all_films()[0]
    assert film.uuid
    new_status = not film.watched
    response = client.post(
        f"/api/set/watched?watch_status={new_status}&uuid={film.uuid}"
    )
    assert response.status_code == 200
    pulled_film = mock_db.get_single_film(film.uuid)
    assert pulled_film.watched == new_status


@pytest.mark.order(216)
def test_api_get_actress_detail(client: TestClient, mock_db: Database) -> None:
    actresses = mock_db.get_actress_list()
    for actress in actresses:
        response = client.get(f"/api/get/actress_detail?name={actress}")
        real_result = mock_db.get_actress_detail(name=actress)
        assert response.status_code == 200
        result: dict[str, Any] = response.json()
        assert result
        assert result.get("name") == actress

        assert len(real_result.films) == len(result.get("films"))
