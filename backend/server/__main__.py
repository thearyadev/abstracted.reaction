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
from uuid import UUID, uuid4
from fastapi import APIRouter, FastAPI, File, Form, Query, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from util.models.film import FilmNoBytes
from typing import Any, MutableMapping


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
        self.filmsStamp: UUID | None = None

        self.images: dict[UUID, bytes] = dict()


class Server:
    def __init__(self, host: str, port: int):
        self.app = FastAPI()
        self.router = APIRouter(prefix="/api")
        self.host = host
        self.port = port
        self.db = database_autoconfigure()
        self.configure_routes()
        self.app.include_router(self.router)

        self.app.mount(
            "/", StaticFileHandler(directory="./server/build", html=True), name="static"
        )

    def configure_routes(self) -> None:
        ...

    def run(self) -> Server:
        uvicorn.run(self.app, host=self.host, port=self.port)
        return self


def main() -> int:
    server = Server(host="0.0.0.0", port=8112).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
