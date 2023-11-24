from psycopg2 import pool
from psycopg2.extras import DictCursor, UUID_adapter, register_uuid
import logging
import os
import random
import time
from pathlib import Path
from uuid import UUID
import psycopg2
import contextlib
from util.models.rating import Rating
from util.models.film import FilmNoBytes
import inspect
from typing import Any, ContextManager, Tuple, Generator, Literal
from util.models.uuid import RecordUUIDLike
import dotenv


def split_rating_and_record(
    film_data: psycopg2.extras.DictRow,
) -> tuple[Rating, dict[str, Any]]:
    """Extracts rating from a psycopg2.extras.DictRow"""
    film_data_as_dict = dict(film_data)
    rating = Rating(
        uuid=film_data_as_dict.pop("r_uuid"),
        average=film_data_as_dict.pop("average"),
        story=film_data_as_dict.pop("story"),
        positions=film_data_as_dict.pop("positions"),
        pussy=film_data_as_dict.pop("pussy"),
        shots=film_data_as_dict.pop("shots"),
        boobs=film_data_as_dict.pop("boobs"),
        face=film_data_as_dict.pop("face"),
        rearview=film_data_as_dict.pop("rearview"),
    )
    return rating, film_data_as_dict


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
        self.db_name = db_name  # db connection credentials
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_port = db_port
        self.min_connections = min_connections  # for connection pool
        self.max_connections = max_connections
        register_uuid()  # allows use of UUID objects in psycopg2
        for attempt in range(1, max_retries + 1):
            try:
                self.connection_pool = pool.SimpleConnectionPool(
                    host=self.db_host,
                    port=self.db_port,
                    dbname=self.db_name,
                    user=self.db_user,
                    password=self.db_password,
                    minconn=self.min_connections,
                    maxconn=self.max_connections,
                )
                break
            except psycopg2.OperationalError as e:
                logging.warning(
                    f"Attempt {attempt} of {max_retries} to connect to database failed. Retrying in {retry_interval}"
                    f"seconds with credentials: {self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}"
                )
                time.sleep(retry_interval)
        else:
            logging.critical(
                f"Failed to connect to database after {max_retries} attempts. Exiting."
            )
            raise SystemExit(1)

        logging.info("Connected to database")

    @contextlib.contextmanager
    def get_db_connection(
        self,
    ) -> Generator[
        Tuple[psycopg2.extensions.connection, psycopg2.extensions.cursor], None, None
    ]:
        conn: psycopg2.extensions.connection = self.connection_pool.getconn()
        cursor: psycopg2.extensions.cursor = conn.cursor(cursor_factory=DictCursor)
        with conn, cursor:
            yield conn, cursor

    def get_latest_commit_uuid(self) -> UUID | None:
        """Returns the UUID of the latest commit"""
        with self.get_db_connection() as (conn, cur):
            cur.execute(
                "SELECT uuid FROM public.history ORDER BY timestamp DESC LIMIT 1;"
            )
            try:
                data: tuple[UUID] = cur.fetchone()  # type: ignore
                return data[0]
            except IndexError:
                return None

    def database_init(self, schema: str) -> None:
        """Creates tables if they don't exist. Runs on production; ensure schema is clean."""
        with self.get_db_connection() as (conn, cur):
            cur.execute(schema)
            conn.commit()
        logging.info("Database initialized")

    def get_all_films(self) -> list[FilmNoBytes]:
        """Returns all films in the database"""
        with self.get_db_connection() as (conn, cur):
            cur.execute(
                """SELECT f.uuid, f.title, f.date_added, f.filename, f.watched, f.state, f.actresses, r.uuid AS r_uuid, r.*
                    FROM public.film f
                    JOIN public.rating r ON f.rating = r.uuid;

                            """
            )
            # type behaviour is changed due to psycopg2.extras.DictCursor used in get_db_connection
            films_data_including_rating: list[psycopg2.extras.DictRow] = cur.fetchall()  # type: ignore
            output = list()

            for film in films_data_including_rating:
                rating, film_data = split_rating_and_record(film)
                output.append(FilmNoBytes(rating=rating, **film_data))
            return output

    def get_single_film(self, uuid: RecordUUIDLike) -> FilmNoBytes:
        """Returns a single film from the database"""
        with self.get_db_connection() as (conn, cur):
            cur.execute(
                """SELECT f.uuid, f.title, f.date_added, f.filename, f.watched, f.state, f.actresses, r.uuid AS r_uuid, r.*
                    FROM public.film f
                    JOIN public.rating r ON f.rating = r.uuid
                    WHERE f.uuid = %s;
                            """,
                (uuid,),
            )
            # type behaviour is changed due to psycopg2.extras.DictCursor used in get_db_connection
            film_data_including_rating: psycopg2.extras.DictRow = cur.fetchone()  # type: ignore
            rating, film_data = split_rating_and_record(film_data_including_rating)
            return FilmNoBytes(rating=rating, **film_data)

    def update_film(self, new_film_data: FilmNoBytes) -> None:
        """Will update all fields. If a FilmNoBytes object is received, the thumbnail and poster will not be altered.
        This will also update the rating object."""
        ...

    def get_image(
        self, uuid: RecordUUIDLike, image_type: Literal["POSTER", "THUMBNAIL"]
    ) -> bytes:
        ...


def database_autoconfigure() -> Database:
    """Returns a Database object with credentials from environment variables"""
    # TODO: ensure env vars are set, if not, load them using dotenv.
    # TODO: fix type usage
    dotenv.load_dotenv()

    return Database(
        db_name=os.getenv("POSTGRES_DB"),  # type: ignore
        db_user=os.getenv("POSTGRES_USER"),  # type: ignore
        db_password=os.getenv("POSTGRES_PASSWORD"),  # type: ignore
        db_host=os.getenv("POSTGRES_HOST"),  # type: ignore
        db_port=os.getenv("POSTGRES_PORT"),  # type: ignore
        max_connections=int(os.getenv("POSTGRES_MAX_CONNECTIONS")),  # type: ignore
        min_connections=int(os.getenv("POSTGRES_MIN_CONNECTIONS")),  # type: ignore
        max_retries=int(os.getenv("POSTGRES_MAX_RETRIES")),  # type: ignore
        retry_interval=int(os.getenv("POSTGRES_RETRY_INTERVAL")),  # type: ignore
    )


if __name__ == "__main__":
    ...
