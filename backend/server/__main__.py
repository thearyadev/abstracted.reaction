from __future__ import annotations

import uvicorn
import fastapi
from util.database.database import Database
import datetime
import logging
import os
import time
from pathlib import Path
import shutil
from fastapi import (
    APIRouter,
    FastAPI,
    File,
    Form,
    Query,
    UploadFile,
    HTTPException,
    Body,
)
from fastapi.responses import FileResponse, HTMLResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from util.models.film import FilmNoBytes
from typing import Any, MutableMapping
from util.models.uuid import RecordUUIDLike
from util.models.rating import Rating
from util.models.actress_detail import ActressDetail
from typing import Literal
from fastapi.testclient import TestClient
from typing import Annotated, Optional


class StaticFileHandler(StaticFiles):
    async def get_response(
            self, path: str, scope: MutableMapping[str, Any]
    ) -> Response:
        """
        Override method StaticFiles.get_response.
        This method is called for the lookup of a static file.
        Calls the super method, if it fails, return index.html
        :param path:
        :param scope:
        :return:
        """
        try:
            return await super().get_response(path, scope)
        except fastapi.exceptions.HTTPException as e:
            if e.status_code == 404:
                return await super().get_response("index.html", scope)
            else:
                raise e


class DatabaseReadCache:
    def __init__(self) -> None:
        self.films: list[FilmNoBytes] = list()
        self.filmsStamp: RecordUUIDLike | None = None
        self.images: dict[RecordUUIDLike, bytes] = dict()


class Server:
    def __init__(self, host: str, port: int, db: Database | None = None):
        self.app = FastAPI()
        self.router = APIRouter(prefix="/api")
        self.host = host
        self.port = port
        self.db = Database.from_env(load_dot_env=True)
        self.cache = DatabaseReadCache()
        self.configure_routes()
        self.media_path = Path(os.environ['APP_FILM_PATH'])
        assert self.media_path.exists()  # provided path doesnt exist

        self.app.include_router(self.router)
        # self.app.mount(
        #     "/", StaticFileHandler(directory="./server/build", html=True), name="static"
        # )

    def test_client(self) -> TestClient:
        return TestClient(self.app)

    def configure_routes(self) -> None:
        self.router.add_api_route(
            "/get/films",
            self.get_all_films,
            methods=["GET"],
        )
        self.router.add_api_route(
            "/get/film",
            self.get_single_film,
            methods=["GET"],
            responses={404: {"description": "film not found"}},
        )
        self.router.add_api_route(
            "/get/image",
            self.get_image,
            methods=["GET"],
            responses={404: {"description": "film not found"}},
        )
        self.router.add_api_route(
            "/set/rating",
            self.set_rating,
            methods=["POST"],
            responses={404: {"description": "rating not found"}},
        )
        self.router.add_api_route(
            "/set/delete",
            self.delete_film,
            methods=["POST"],
            responses={500: {"description": "deletion error"}},
        )
        self.router.add_api_route(
            "/set/watched",
            self.set_watch_status,
            methods=["POST"],
            responses={404: {"description": "film not found"}},
        )
        self.router.add_api_route(
            "/get/actresses", self.get_actress_list, methods=["GET"]
        )
        self.router.add_api_route(
            "/get/video", self.serve_video, methods=['GET'], responses={404: {"description": "film not found"}}
        )

    def run(self) -> Server:  # pragma: no cover
        logging.info(f"Starting uvicorn server on {self.host}:{self.port}")
        uvicorn.run(self.app, host=self.host, port=self.port)
        return self

    def get_all_films(self) -> list[FilmNoBytes]:
        if (latestStamp := self.db.get_latest_commit_uuid()) != self.cache.filmsStamp:
            self.cache.filmsStamp, self.cache.films = (
                latestStamp,
                self.db.get_all_films(),
            )
        return self.cache.films

    def get_single_film(self, uuid: RecordUUIDLike = Query(...)) -> FilmNoBytes:
        if retrievedEntry := self.db.get_single_film(uuid):
            return retrievedEntry
        raise HTTPException(status_code=404, detail="film not found")

    def get_image(
            self,
            uuid: RecordUUIDLike = Query(...),
            image_type: Literal["THUMBNAIL", "POSTER"] = Query(...),
    ) -> Response:
        image: bytes | None = None
        if (
                image_type == "THUMBNAIL"
        ):  # thumbnail is retrieved from cache, poster is not.
            image = self.cache.images.get(uuid, None)
            if image is None:
                pulled_image: bytes | None = self.db.get_thumbnail(uuid)
                if pulled_image is None:
                    raise HTTPException(404, "film not found")
                image = pulled_image
                self.cache.images[uuid] = image

        if image_type == "POSTER":
            pulled_image = self.db.get_poster(uuid)
            if pulled_image is None:
                raise HTTPException(404, "film not found")
            image = pulled_image

        return Response(image, media_type="image/png")

    def set_rating(self, rating: Annotated[Rating, Body(embed=True)]) -> Response:
        try:
            self.db.update_rating(rating)
            return Response(status_code=200)
        except ValueError:
            raise HTTPException(status_code=404, detail="rating not found")

    def delete_film(self, uuid: RecordUUIDLike = Query(...)) -> Response:
        try:
            self.db.delete_film(uuid=uuid)
            return Response(status_code=200)
        except IOError:
            raise HTTPException(status_code=500, detail="deletion failed")

    def set_watch_status(
            self, watch_status: bool = Query(...), uuid: RecordUUIDLike = Query(...)
    ) -> Response:
        film = self.db.get_single_film(uuid)
        if not film:
            raise HTTPException(status_code=404, detail="film not found")
        film.watched = watch_status
        self.db.update_film(film)
        return Response(status_code=200)

    def get_actress_list(self) -> list[str]:
        return self.db.get_actress_list()

    def get_actress_detail(self, name: str = Query(...)) -> ActressDetail:
        return NotImplemented

    def serve_video(self, uuid: RecordUUIDLike = Query(...), filename: Optional[str] = Query(...)) -> FileResponse:
        try:
            # use filename optional arg to optimize and reduce database calls.
            # if filename is not present, use database calls.
            return FileResponse(
                self.media_path / self.db.get_single_film(uuid).filename if not filename else filename,
                media_type="video/mp4",
                headers={"Accept-Ranges": "bytes"}
            )
        except* (AttributeError, TypeError):
            # attribute error if film not found, type error if film not found and filename is none
            raise HTTPException(status_code=404, detail="film not found")

    def serve_root(self, *_: tuple[Any]) -> HTMLResponse:
        return NotImplemented


def main() -> int:  # pragma: no cover
    server = Server(host="0.0.0.0", port=8112).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
