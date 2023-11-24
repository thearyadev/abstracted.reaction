import dataclasses
from uuid import UUID


@dataclasses.dataclass
class Rating:
    uuid: str | None
    average: float
    story: int
    positions: int
    pussy: int
    shots: int
    boobs: int
    face: int
    rearview: int
