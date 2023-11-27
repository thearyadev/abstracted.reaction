import psycopg
from psycopg import Cursor
from typing import Sequence, Any, Generator, Iterator, TypeAlias, Tuple, ContextManager

import psycopg_pool
import os
from psycopg.rows import class_row
import contextlib

from uuid import UUID
import logging
import sys

from util.models.rating import Rating
from util.models.film import FilmNoBytes, Film, FilmState
from util.models.uuid import RecordUUIDLike
from dataclasses import fields

Record: TypeAlias = Film | FilmNoBytes | Rating


def split_rating_and_record(
    film_data: dict[str, Any],
) -> tuple[Rating, dict[str, Any]]:
    """Extracts rating from a psycopg2.extras.DictRow"""
    rating = Rating(
        uuid=film_data.pop("r_uuid"),
        average=film_data.pop("average"),
        story=film_data.pop("story"),
        positions=film_data.pop("positions"),
        pussy=film_data.pop("pussy"),
        shots=film_data.pop("shots"),
        boobs=film_data.pop("boobs"),
        face=film_data.pop("face"),
        rearview=film_data.pop("rearview"),
    )
    return rating, film_data


class DictRowFactory:
    def __init__(self, cursor: Cursor[Any]):
        self.fields = (
            [c.name for c in cursor.description]
            if cursor.description is not None
            else None
        )

    def __call__(self, values: Sequence[Any]) -> dict[str, Any]:
        return dict(zip(self.fields, values))


class Database:
    def __init__(
        self,
        db_name: str,
        db_user: str,
        db_password: str,
        db_host: str,
        db_port: str,
        max_connections: int,
        min_connections: int,
        max_retries: int,
        retry_interval: int,
    ) -> None:
        self.pool = psycopg_pool.ConnectionPool(
            f"""        
            dbname={db_name}
            user={db_user}
            password={db_password}
            host={db_host}
            port={db_port}
        """,
            open=True,
        )
        self.pool.wait(timeout=60)

    def get_latest_commit_uuid(self) -> UUID | None:
        """Returns the UUID of the latest commit"""
        with self.pool.connection() as conn, conn.cursor(
            row_factory=DictRowFactory
        ) as cur:
            cur.execute(
                "SELECT uuid FROM public.history ORDER BY timestamp DESC LIMIT 1;"
            )
            if (result := cur.fetchone()) is not None:
                return result["uuid"]
            return None

    def database_init(self, schema: str) -> None:
        """Creates tables if they don't exist. Runs on production; ensure schema is clean."""
        with self.pool.connection() as conn, conn.cursor(
            row_factory=DictRowFactory
        ) as cur:
            cur.execute(schema)
        logging.info("Database initialized")

    def get_all_films(self) -> list[FilmNoBytes]:
        """Returns all films in the database"""
        with self.pool.connection() as conn, conn.cursor(
            row_factory=DictRowFactory
        ) as cur:
            cur.execute(
                """SELECT f.uuid, f.title, f.date_added, f.filename, f.watched, f.state, f.actresses,
                 r.uuid as "r_uuid", r.average, r.boobs, r.face, r.rearview, r.shots,
                 r.story, r.positions, r.pussy
                    FROM public.film f
                    JOIN public.rating r ON f.rating = r.uuid;
                """
            )
            # type behaviour is changed due to psycopg2.extras.DictCursor used in get_db_connection
            films_data_including_rating: list[dict] = cur.fetchall()  # type: ignore
            output = list()
            for film in films_data_including_rating:
                rating, film_data = split_rating_and_record(film)
                output.append(FilmNoBytes(rating=rating, **film_data))
            return output

    def get_single_film(self, uuid: RecordUUIDLike) -> FilmNoBytes | None:
        """Returns a single film from the database"""

        with self.pool.connection() as conn, conn.cursor(
            row_factory=DictRowFactory
        ) as cur:
            cur.execute(
                """SELECT f.uuid, f.title, f.date_added, f.filename, f.watched, f.state, f.actresses,
                 r.uuid as "r_uuid", r.average, r.boobs, r.average, r.face, r.rearview, r.shots,
                 r.story, r.positions, r.pussy
                    FROM public.film f
                    JOIN public.rating r ON f.rating = r.uuid
                    WHERE f.uuid = %s;
                            """,
                (uuid,),
            )
            # type behaviour is changed due to psycopg2.extras.DictCursor used in get_db_connection
            film_data_including_rating: dict | None = cur.fetchone()  # type: ignore
            if film_data_including_rating is None:
                return None
            rating, film_data = split_rating_and_record(film_data_including_rating)
            return FilmNoBytes(
                rating=rating,
                state=FilmState.__members__[film_data.pop("state")],
                **film_data,
            )

    def get_thumbnail(self, uuid: RecordUUIDLike) -> memoryview | None:
        with self.pool.connection() as conn, conn.cursor(
            row_factory=DictRowFactory
        ) as cur:
            cur.execute(
                """
                    SELECT thumbnail FROM film WHERE uuid = %s
                    """,
                (uuid,),
            )
            image: dict | None = cur.fetchone()  # type: ignore
            if image is None:
                return None
            ret: memoryview = image["thumbnail"]
            return ret

    def get_poster(self, uuid: RecordUUIDLike) -> memoryview | None:
        with self.pool.connection() as conn, conn.cursor(
            row_factory=DictRowFactory
        ) as cur:
            cur.execute(
                """
                SELECT poster FROM film WHERE uuid = %s
                """,
                (uuid,),
            )
            image: psycopg2.extras.DictRow | None = cur.fetchone()  # type: ignore
            if image is None:
                return None
            ret: memoryview = image["poster"]
            return ret

    def insert_film(self, new_film: Film) -> RecordUUIDLike:
        with self.pool.connection() as conn, conn.cursor() as cur:
            cur.execute(
                """
                WITH rating_record_uuid AS (
                    INSERT INTO rating (average, story, positions, pussy, shots, boobs, face, rearview) 
                    VALUES (0.0, 0, 0, 0, 0, 0, 0, 0)
                    RETURNING uuid
                )
                INSERT INTO film (title, date_added, filename, watched, state, thumbnail, poster, actresses, rating) 
                SELECT %s, %s, %s, %s, %s, %s, %s, %s, uuid
                FROM rating_record_uuid
                RETURNING uuid;
                """,
                (
                    new_film.title,
                    new_film.date_added,
                    new_film.filename,
                    new_film.watched,
                    new_film.state,
                    new_film.thumbnail,
                    new_film.poster,
                    new_film.actresses,
                ),
            )
            return cur.fetchone()[0]

    def update_film(self, new_film_data: FilmNoBytes) -> None:
        with self.pool.connection() as conn, conn.cursor() as cur:
            cur.execute(
                """
                UPDATE public.film
                SET title = %s, date_added = %s, filename = %s, watched = %s, state = %s, actresses = %s
                WHERE uuid = %s
                RETURNING uuid;
                """,
                (
                    new_film_data.title,
                    new_film_data.date_added,
                    new_film_data.filename,
                    new_film_data.watched,
                    new_film_data.state,
                    new_film_data.actresses,
                    new_film_data.uuid,
                ),
            )
            try:
                assert (
                    cur.fetchone()
                )  # This will raise an AssertionError if the film doesn't exist.
            except AssertionError:
                raise ValueError("film does not exist")

    def update_rating(self, new_rating_data: Rating) -> None:
        with self.pool.connection() as conn, conn.cursor(
            row_factory=DictRowFactory
        ) as cur:
            cur.execute(
                """ 
                UPDATE RATING
                SET  story = %s, positions = %s,
                pussy = %s, shots = %s, boobs = %s, face = %s, rearview = %s
                WHERE uuid = %s RETURNING uuid;
                """,
                (new_rating_data.story, new_rating_data.positions, new_rating_data.pussy, new_rating_data.shots,
                 new_rating_data.boobs, new_rating_data.face, new_rating_data.rearview, new_rating_data.uuid),
            )

            try:
                assert (
                    cur.fetchone()
                )  # This will raise an AssertionError if the rating doesn't exist.
            except AssertionError:
                raise ValueError("rating does not exist")

