import dataclasses
from datetime import datetime
from enum import Enum

from util.models.rating import Rating
from util.models.uuid import RecordUUIDLikeNullable


class FilmState(Enum):
    NOT_TRANSCODED = "NOT_TRANSCODED"
    TRANSCODING = "TRANSCODING"
    COMPLETE = "COMPLETE"


@dataclasses.dataclass
class FilmNoBytes:
    uuid: RecordUUIDLikeNullable
    title: str
    date_added: datetime
    filename: str
    watched: bool
    state: FilmState
    rating: Rating
    actresses: list[str]


@dataclasses.dataclass
class Film(FilmNoBytes):
    thumbnail: bytes
    poster: bytes
    rating: Rating | None  # type: ignore
    # type ignored because I disagree.
