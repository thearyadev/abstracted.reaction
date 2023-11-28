from util.database.database import Database
import pytest
from .test_database import mock_db
from fastapi.testclient import TestClient
from server.__main__ import Server
from pathlib import Path
from uuid import uuid4
import httpx
import datetime


@pytest.fixture(scope="module")
def client(mock_db: Database) -> TestClient:
    server = Server(host="0.0.0.0", port=9761)  # host and port unused in this context.
    mock_db.database_init(Path("./util/database/schema.sql").read_text())
    server.db = mock_db
    return server.test_client()


@pytest.mark.order(16)
def test_api_films_empty(client: TestClient) -> None:
    response = client.get("/api/get/films")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert not len(response.json())


@pytest.mark.order(17)
def test_api_film_no_result(client: TestClient) -> None:
    response = client.get(f"/api/get/film?uuid={uuid4()}")
    assert response.status_code == 404
    assert response.json() == {"detail": "film not found"}


@pytest.mark.order(18)
def test_api_image_doesnt_exist(client: TestClient) -> None:
    poster_response = client.get(f"/api/get/image?uuid={uuid4()}&image_type=POSTER")
    thumbnail_response = client.get(
        f"/api/get/image?uuid={uuid4()}&image_type=THUMBNAIL"
    )
    assert poster_response.status_code == 404
    assert poster_response.json() == {"detail": "film not found"}
    assert thumbnail_response.status_code == 404
    assert thumbnail_response.json() == {"detail": "film not found"}


@pytest.mark.order(19)
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


@pytest.mark.order(20)
def test_api_delete_film_doesnt_exist(client: TestClient) -> None:
    response = client.post(
        "/api/set/delete",
        json={
            "film": {
                "uuid": str(uuid4()),
                "title": "test_title",
                "date_added": datetime.datetime.now().isoformat(),
                "filename": "test_filename",
                "watched": "false",
                "state": "TRANSCODING",
                "rating": {
                    "uuid": str(uuid4()),
                    "average": 10,
                    "story": 10,
                    "positions": 10,
                    "pussy": 10,
                    "shots": 10,
                    "boobs": 10,
                    "face": 10,
                    "rearview": 10,
                },
                "actresses": ["test0", "test2"],
            }
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "film not found"}


@pytest.mark.order(21)
def test_api_set_watch_status_doesent_exist(client: TestClient) -> None:
    response = client.post(f"/api/set/watched?uuid={uuid4()}&watch_status={True}")
    assert response.status_code == 404
    assert response.json() == {"detail": "film not found"}


@pytest.mark.order(22)
def test_api_get_actress_list_no_entries(client: TestClient) -> None:
    response = client.get("/api/get/actresses")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert not len(response.json())
