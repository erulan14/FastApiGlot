import datetime

from ..db.mongodb import AsyncIOMotorClient
from pydantic import EmailStr
from bson.objectid import ObjectId

from ..core.config import database_name, users_collection_name
from ..models.user import UserInCreate, UserInDB, UserInUpdate


async def get_users(conn: AsyncIOMotorClient) -> list[UserInDB]:
    users: list[UserInDB] = []
    users_docs = conn[database_name][users_collection_name].find()

    async for row in users_docs:
        users.append(
            UserInDB(**row)
        )

    return users


async def get_user(conn: AsyncIOMotorClient, username: str) -> UserInDB:
    row = await conn[database_name][users_collection_name].find_one({"username": username})
    if row:
        return UserInDB(**row)


async def get_user_by_id(conn: AsyncIOMotorClient, id: str) -> UserInDB:
    row = await conn[database_name][users_collection_name].find_one({"_id": ObjectId(id)})
    if row:
        return UserInDB(**row)


async def get_user_by_email(conn: AsyncIOMotorClient, email: EmailStr) -> UserInDB:
    row = await conn[database_name][users_collection_name].find_one({"email": email})
    if row:
        return UserInDB(**row)


async def get_user_by_username(conn: AsyncIOMotorClient, username: str) -> UserInDB:
    row = await conn[database_name][users_collection_name].find_one({"username": username})
    if row:
        return UserInDB(**row)


async def create_user(conn: AsyncIOMotorClient, user: UserInCreate) -> UserInDB:
    dbuser = UserInDB(**user.dict())
    dbuser.change_password(user.password)
    dbuser.created_at = ObjectId(dbuser.id).generation_time
    dbuser.updated_at = ObjectId(dbuser.id).generation_time

    row = await conn[database_name][users_collection_name].insert_one(dbuser.dict())

    dbuser.id = row.inserted_id
    return dbuser


async def update_user(conn: AsyncIOMotorClient, username: str, user: UserInUpdate) -> UserInDB:
    dbuser = await get_user(conn, username)

    dbuser.username = user.username or dbuser.username
    dbuser.email = user.email or dbuser.email
    dbuser.is_active = user.is_active or dbuser.is_active
    dbuser.is_personal = user.is_personal or dbuser.is_personal
    dbuser.is_superuser = user.is_superuser or dbuser.is_superuser
    dbuser.first_name = user.first_name or dbuser.first_name
    dbuser.last_name = user.last_name or dbuser.last_name
    dbuser.user_permission = user.user_permission or dbuser.user_permission
    dbuser.image = user.image or dbuser.image
    dbuser.updated_at = datetime.datetime.now() # ObjectId(dbuser.id).generation_time
    if user.password:
        dbuser.change_password(user.password)

    updated_at = await conn[database_name][users_collection_name]\
        .update_one({"username": dbuser.username}, {'$set': dbuser.dict()})
    dbuser.updated_at = updated_at
    return dbuser


async def delete_user(conn: AsyncIOMotorClient, id: str):
    dbuser = await get_user_by_id(conn, id)
    if dbuser:
        delete_result = await conn[database_name][users_collection_name].delete_one({"_id": ObjectId(dbuser.id)})
        if delete_result.deleted_count == 1:
            return True

    return False

    #await conn[database_name][users_collection_name].