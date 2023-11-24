import dataclasses
from uuid import UUID
from datetime import datetime
from enum import Enum, auto
from util.models.rating import Rating
from util.models.uuid import RecordUUIDLikeNullable


class FilmState(Enum):
    NOT_TRANSCODED = auto()
    TRANSCODING = auto()
    COMPLETE = auto()


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
