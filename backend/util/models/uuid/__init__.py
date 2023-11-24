import uuid
from typing import TypeAlias, Union

RecordUUIDLikeNullable: TypeAlias = Union[str, uuid.UUID, None]
RecordUUIDLike: TypeAlias = Union[str, uuid.UUID]
