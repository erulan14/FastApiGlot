from typing import Optional
from pydantic import Field
from .dbmodel import DBModelMixin, DateTimeModelMixin, PyObjectId
from .rwmodel import RWModel


class DeviceModel(RWModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    company: str
    port: int


class DeviceInDB(DBModelMixin, DeviceModel):
    pass


class Device(DeviceModel):
    pass


class DevicesModel(RWModel):
    devices: list[Device]


class DeviceInCreate(DeviceModel):
    pass


class DeviceInResponse(RWModel):
    device: Device


class DeviceInUpdate(RWModel):
    name: Optional[str] = None
    company: Optional[str] = None
    port: Optional[str] = None
