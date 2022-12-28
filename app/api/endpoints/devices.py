from fastapi import APIRouter, Body, Depends, Response
import json

from ...core.jwt import JWTBearer
from ...crud.devices import get_devices, create_devices_db, update_device_db
from ...db.mongodb import AsyncIOMotorClient, get_database
from ...models.devices import DeviceModel, DeviceInDB, DeviceInCreate, DevicesModel, DeviceInResponse
from ...core.utils import create_aliased_response

router = APIRouter()


@router.get('/devices/', response_model=DevicesModel, tags=["devices"], dependencies=[Depends(JWTBearer())])
async def get_devices_list(db: AsyncIOMotorClient = Depends(get_database)):
    devices = await get_devices(db)
    db_devices = DevicesModel(devices=devices).devices
    return create_aliased_response(db_devices)


@router.get('/devices/{id}', response_model=DevicesModel, tags=["devices"], dependencies=[Depends(JWTBearer())])
async def get_device(id: str, db: AsyncIOMotorClient = Depends(get_database)):
    print(id)
    return Response("{}".format(id), media_type="application/json")


@router.post('/devices/', response_model=DeviceInCreate, tags=["devices"], dependencies=[Depends(JWTBearer())])
async def create_new_device(device: DeviceInCreate = Body(..., embed=True), db: AsyncIOMotorClient = Depends(get_database)):
    db_device = await create_devices_db(db, device)
    return Response(json.dumps(db_device.dict()), media_type="application/json")


@router.put('/devices/', tags=["devices"], dependencies=[Depends(JWTBearer())])
async def update_device(db: AsyncIOMotorClient = Depends(get_database), id: str | None = None):
    db_device = await update_device_db(db, id)
    return  Response(json.dumps(db_device.dict()), media_type="application/json")