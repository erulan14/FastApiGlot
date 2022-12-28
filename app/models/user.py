from typing import Optional
from bson import ObjectId
from pydantic import EmailStr, HttpUrl, Field

from .dbmodel import DBModelMixin, PyObjectId
from .rwmodel import RWModel
from ..core.security import generate_salt, get_password_hash, verify_password


class UserBase(RWModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str
    email: EmailStr
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_personal: Optional[bool] = None
    user_permission: Optional[list] = []
    image: Optional[HttpUrl] = None

    class Config:
        json_encoders = {ObjectId: str}


class UserInDB(UserBase):
    salt: str = ""
    hashed_password: str = ""

    def check_password(self, password: str):
        return verify_password(self.salt + password, self.hashed_password)

    def change_password(self, password: str):
        self.salt = generate_salt()
        self.hashed_password = get_password_hash(self.salt + password)


class UserModel(UserBase):
    pass


class User(UserBase):
    token: str


class Users(RWModel):
    users: list[UserModel]


class UserInResponse(RWModel):
    user: User


class UserInLogin(RWModel):
    username: str
    password: str


class UserInCreate(UserInLogin):
    username: str
    email: EmailStr


class UserInUpdate(RWModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_personal: Optional[bool] = None
    user_permission: Optional[list] = []
    image: Optional[HttpUrl] = None