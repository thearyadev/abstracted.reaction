import dataclasses

from util.models.uuid import RecordUUIDLikeNullable


@dataclasses.dataclass
class Rating:
    uuid: RecordUUIDLikeNullable
    average: float
    story: int
    positions: int
    pussy: int
    shots: int
    boobs: int
    face: int
    rearview: int
