from .rwmodel import RWModel
from .dbmodel import PyObjectId
from pydantic import Field


class Pos(RWModel):
    x: float
    y: float
    z: int
    a: int
    s: int
    st: int


class Message(RWModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    n: int
    t: int
    pos: Pos
    p: dict[int, int]


class MessageInDB(Message):
    pass


class Messages(RWModel):
    messages: list[Message]
