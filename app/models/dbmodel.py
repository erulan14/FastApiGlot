from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from bson import ObjectId
import json


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return str(ObjectId(v))

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class DateTimeModelMixin(BaseModel):
    created_at: Optional[datetime] #= Field(..., alias="createdAt")
    updated_at: Optional[datetime] #= Field(..., alias="updatedAt")


class DBModelMixin(DateTimeModelMixin):
    #id: Optional[int] = None
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")