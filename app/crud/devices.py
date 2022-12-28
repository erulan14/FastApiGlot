from ..db.mongodb import AsyncIOMotorClient
from pydantic import EmailStr
from bson.objectid import ObjectId

from ..core.config import database_name, device_collection_name
from ..models.devices import DeviceModel, DeviceInDB, DeviceInCreate, DevicesModel, DeviceInUpdate


async def get_device(conn: AsyncIOMotorClient, id: str) -> DeviceInDB:
    row = await conn[database_name][device_collection_name].find_one({"_id": id})
    if row:
        return DeviceInDB(**row)


async def get_devices(conn: AsyncIOMotorClient, limit=20, offset=0) -> list[DeviceInDB]:
    devices: list[DeviceInDB] = []
    devices_docs = conn[database_name][device_collection_name].find(limit=limit, skip=offset)

    async for row in devices_docs:
        devices.append(
            DeviceInDB(
                **row
            )
        )

    #print(devices)

    return devices


async def create_devices_db(conn: AsyncIOMotorClient, article: DeviceInCreate) -> DeviceInDB:
    device_doc = article.dict()
    await conn[database_name][device_collection_name].insert_one(device_doc)

    return DeviceInDB(
        **device_doc
    )


async def update_device_db(conn: AsyncIOMotorClient, id: str, device: DeviceInUpdate) -> DeviceInDB:
    db_device = await get_device(id)

    db_device.name = device.name or db_device.name
    db_device.company = device.company or db_device.company
    db_device.port = device.port or db_device.port

    await conn[database_name][device_collection_name].update_one({"_id": id}, {"$set": db_device.dict()})

    return db_device