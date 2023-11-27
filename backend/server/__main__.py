from __future__ import annotations

import uvicorn
import fastapi
from util.database.database import database_autoconfigure
import datetime
import logging
import os
import time
from pathlib import Path
import shutil
from fastapi import APIRouter, FastAPI, File, Form, Query, UploadFile, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from util.models.film import FilmNoBytes
from typing import Any, MutableMapping
from util.models.uuid import RecordUUIDLike
from util.models.rating import Rating
from util.models.actress_detail import ActressDetail
from typing import Literal


class StaticFileHandler(StaticFiles):
    async def get_response(
        self, path: str, scope: MutableMapping[str, Any]
    ) -> Response:
        try:
            return await super().get_response(path, scope)
        except fastapi.exceptions.HTTPException as ex:
            if ex.status_code == 404:
                return await super().get_response("index.html", scope)
            else:
                raise ex


class DatabaseReadCache:
    def __init__(self) -> None:
        self.films: list[FilmNoBytes] = list()
        self.filmsStamp: RecordUUIDLike | None = None
        self.images: dict[RecordUUIDLike, bytes] = dict()


class Server:
    def __init__(self, host: str, port: int):
        self.app = FastAPI()
        self.router = APIRouter(prefix="/api")
        self.host = host
        self.port = port
        self.db = database_autoconfigure()
        self.cache = DatabaseReadCache()
        self.configure_routes()

        self.app.include_router(self.router)
        # self.app.mount(
        #     "/", StaticFileHandler(directory="./server/build", html=True), name="static"
        # )

    def configure_routes(self) -> None:
        self.router.add_api_route(
            "/films",
            self.get_all_films,
            methods=["GET"],
        )
        self.router.add_api_route("/film", self.get_single_film, methods=["GET"])
        self.router.add_api_route("/image", self.get_image, methods=["GET"])

        self.router.add_api_route("/delete", self.delete_film, methods=["DELETE"])

    def run(self) -> Server:
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
        if image_type == "THUMBNAIL":
            image = self.cache.images.get(uuid, None)
            if image is None:
                pulled_image: memoryview | None = self.db.get_thumbnail(uuid)
                if pulled_image is None:
                    raise HTTPException(404, "film not found")
                image = pulled_image.tobytes()

        if image_type == "POSTER":
            pulled_image = self.db.get_poster(uuid)
            if pulled_image is None:
                raise HTTPException(404, "film not found")
            image = pulled_image.tobytes()

        return Response(image, media_type="image/png")

    def set_rating(
        self, uuid: RecordUUIDLike = Query(...), rating: Rating = Query(...)
    ) -> Response:
        return NotImplemented

    def delete_film(self, uuid: RecordUUIDLike = Query(...)) -> Response:
        return NotImplemented

    def set_watch_status(
        self, uuid: RecordUUIDLike = Query(...), new_watch_status: bool = Query(...)
    ) -> Response:
        return NotImplemented

    def get_actress_list(self) -> list[str]:
        return NotImplemented

    def get_actress_detail(self, name: str = Query(...)) -> ActressDetail:
        return NotImplemented

    def serve_video(self, uuid: RecordUUIDLike = Query(...)) -> FileResponse:
        return NotImplemented

    def serve_root(self, *_: tuple[Any]) -> HTMLResponse:
        return NotImplemented


def main() -> int:
    server = Server(host="0.0.0.0", port=8112).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
