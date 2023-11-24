import dataclasses
from util.models.uuid import RecordUUIDLike


@dataclasses.dataclass
class Rating:
    uuid: RecordUUIDLike
    average: float
    story: int
    positions: int
    pussy: int
    shots: int
    boobs: int
    face: int
    rearview: int
