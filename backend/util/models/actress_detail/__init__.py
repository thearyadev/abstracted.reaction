import dataclasses
from util.models.film import FilmNoBytes


@dataclasses.dataclass
class ActressDetail:
    name: str
    films: list[FilmNoBytes]
