from __future__ import annotations

import logging
import os
from typing import Any, Sequence, TypeAlias
from uuid import UUID

import dotenv
import psycopg
import psycopg_pool
from psycopg import Cursor
from psycopg.rows import class_row

from util.models.actress_detail import ActressDetail
from util.models.film import Film, FilmNoBytes, FilmState
from util.models.rating import Rating
from util.models.uuid import RecordUUIDLike

Record: TypeAlias = Film | FilmNoBytes | Rating


def split_rating_and_record(
    film_data: dict[str, Any],
) -> tuple[Rating, dict[str, Any]]:
    """
    Removes the rating-related objects
    :param film_data: dict row mapped database record
    :return: rating, remaining data
    """
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
        )  # create a list[str] of the column names

    def __call__(self, values: Sequence[Any]) -> dict[str, Any]:
        # in the event that self.fields is None, the __call__ is not called.
        # the self.fields is empty if there are no results
        # and the __call__ is called with a record, if it exists.

        # zip names with tuple positions to make dict
        return dict(zip(self.fields, values))  # type: ignore


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
            open=True,  # ensure connection is open (note: default: True is being removed in the next version of psycopg
        )
        self.pool.wait(timeout=60)

    def get_latest_commit_uuid(self) -> UUID | None:
        """
        Gets the uuid of the latest commit
        :return: uuid - latest commit
        """
        with self.pool.connection() as conn, conn.cursor(
            row_factory=DictRowFactory
        ) as cur:
            cur.execute(
                "SELECT uuid FROM public.history ORDER BY timestamp DESC LIMIT 1;"
            )
            result: dict[str, UUID] | None = cur.fetchone()
            if result is not None:
                return result["uuid"]
            return None

    def database_init(self, schema: str) -> None:
        """Creates tables if they don't exist. Runs on production; ensure schema is clean.
        :param schema: string of initial database schema
        """
        with self.pool.connection() as conn, conn.cursor(
            row_factory=DictRowFactory
        ) as cur:
            cur.execute(schema)
        logging.info("Database initialized")

    def get_all_films(self) -> list[FilmNoBytes]:
        """Returns all films in the database
        :return: list of FilmNoBytes
        """
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
            films_data_including_rating: list[dict[str, Any]] = cur.fetchall()
            output = list()
            for film in films_data_including_rating:
                rating, film_data = split_rating_and_record(film)
                output.append(FilmNoBytes(rating=rating, **film_data))
            return output

    def get_single_film(self, uuid: RecordUUIDLike) -> FilmNoBytes | None:
        """Returns a single film from the database
        :param uuid: uuid of the film record
        :return:
        """

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

    def get_thumbnail(self, uuid: RecordUUIDLike) -> bytes | None:
        """
        gets a thumbnail from the database
        :param uuid: uuid of film record
        :return: memoryview, none if not found.
        """
        with self.pool.connection() as conn, conn.cursor(
            row_factory=DictRowFactory
        ) as cur:
            cur.execute(
                """
                    SELECT thumbnail FROM film WHERE uuid = %s
                    """,
                (uuid,),
            )
            image: dict[str, bytes] | None = cur.fetchone()
            if image is None:
                return None
            return image["thumbnail"]

    def get_poster(self, uuid: RecordUUIDLike) -> memoryview | None:
        """
        gets a thumbnail from the database
        :param uuid: uuid of film record
        :return: memoryview, none if not found.
        """
        with self.pool.connection() as conn, conn.cursor(
            row_factory=DictRowFactory
        ) as cur:
            cur.execute(
                """
                SELECT poster FROM film WHERE uuid = %s;
                """,
                (uuid,),
            )
            image: psycopg2.extras.DictRow | None = cur.fetchone()  # type: ignore
            if image is None:
                return None
            ret: memoryview = image["poster"]
            return ret

    def insert_film(self, new_film: Film) -> RecordUUIDLike:
        """
        inserts a film into the database.
        :param new_film: Film
        :return: FilmNoBytes
        """
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
            result: tuple[UUID] = cur.fetchone()  # type: ignore
            return result[0]

    def update_film(self, new_film_data: FilmNoBytes) -> None:
        """
        Updates the data in the film record.
        Does not change: thumbnail, poster, rating.
        :param new_film_data:
        """
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
        """
        update the rating data.
        :param new_rating_data:
        """
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
                (
                    new_rating_data.story,
                    new_rating_data.positions,
                    new_rating_data.pussy,
                    new_rating_data.shots,
                    new_rating_data.boobs,
                    new_rating_data.face,
                    new_rating_data.rearview,
                    new_rating_data.uuid,
                ),
            )

            try:
                assert (
                    cur.fetchone()
                )  # This will raise an AssertionError if the rating doesn't exist.
            except AssertionError:
                raise ValueError("rating does not exist")

    def get_actress_list(self) -> list[str]:
        """
        gets the list of actresses in the database
        :return:
        """
        with self.pool.connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT DISTINCT unnest(actresses) FROM film;")
            pulled: list[tuple[str]] = cur.fetchall()
            return [i[0] for i in pulled]

    def get_actress_detail(self, name: str) -> ActressDetail:
        with self.pool.connection() as conn, conn.cursor(
            row_factory=DictRowFactory
        ) as cur:
            cur.execute(
                """
                 SELECT f.uuid, f.title, f.date_added, f.filename, f.watched, f.state, f.actresses,
                 r.uuid as "r_uuid", r.average, r.boobs, r.average, r.face, r.rearview, r.shots,
                 r.story, r.positions, r.pussy
                    FROM public.film f
                    JOIN public.rating r ON f.rating = r.uuid
                    WHERE %s = ANY(f.actresses);
            """,
                (name,),
            )
            films_data: list[dict[str, Any]] = cur.fetchall()
            output = list()
            for film in films_data:
                rating, film_data = split_rating_and_record(film)
                output.append(FilmNoBytes(rating=rating, **film_data))
            return ActressDetail(name=name, films=output)

    def delete_film(self, uuid: RecordUUIDLike) -> None:
        """
        deletes a film from the database. Does not handle file deletion
        :param uuid:
        :param film:
        """

        with self.pool.connection() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM film WHERE uuid = %s", (uuid,))
            conn.commit()

    def get_not_transcoded_and_set_transcoding(self) -> FilmNoBytes | None:
        with self.pool.connection() as conn, conn.cursor(
            row_factory=DictRowFactory
        ) as cur:
            cur.execute(
                """
            SELECT f.uuid, f.title, f.date_added, f.filename, f.watched, f.state, f.actresses,
                 r.uuid as "r_uuid", r.average, r.boobs, r.average, r.face, r.rearview, r.shots,
                 r.story, r.positions, r.pussy 
             FROM film f
             JOIN rating r ON f.rating = r.uuid
            WHERE state = %s FOR UPDATE SKIP LOCKED LIMIT 1;
            """,
                (FilmState.NOT_TRANSCODED,),
            )
            result: dict[str, Any] | None = cur.fetchone()

            if result is None:
                return None
            rating, remaining = split_rating_and_record(result)

            ret = FilmNoBytes(rating=rating, **remaining)
            ret.state = FilmState.TRANSCODING
            cur.execute(
                """
            UPDATE film SET state = %s WHERE uuid = %s
           """,
                (ret.state, ret.uuid),
            )

            return ret

    @classmethod
    def from_env(cls, load_dot_env: bool = False) -> Database:  # pragma: no cover
        """
        Builds a Database instance using pre-defined strings in the local environment.
        If load_dot_env is True, dotenv.load_env() will be run to retrieve the environment vars from .env file.
        :param load_dot_env:
        :return:
        """
        if load_dot_env:
            assert dotenv.load_dotenv()
        try:
            return Database(
                db_name=os.environ["POSTGRES_DB"],
                db_user=os.environ["POSTGRES_USER"],
                db_password=os.environ["POSTGRES_PASSWORD"],
                db_host=os.environ["POSTGRES_HOST"],
                db_port=os.environ["POSTGRES_PORT"],
                max_retries=int(os.environ["POSTGRES_MAX_RETRIES"]),
                max_connections=int(os.environ["POSTGRES_MAX_CONNECTIONS"]),
                min_connections=int(os.environ["POSTGRES_MIN_CONNECTIONS"]),
                retry_interval=int(os.environ["POSTGRES_RETRY_INTERVAL"]),
            )
        except* (KeyError, ValueError):
            logging.critical("Environment variables are not correctly configured.")
            raise
