from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from ...core.jwt import JWTBearer
from ...db.mongodb import AsyncIOMotorClient, get_database
from ...crud.messages import get_messages_by_id
from ...models.messages import Messages

router = APIRouter()


@router.get("/messages/{id}", tags=["messages"], dependencies=[Depends(JWTBearer())])
async def get_messages_id(id: int, limit: int = Query(20, gt=0),
                          from_time: int = Query(0),
                          to_time: int = Query(0),
                          db: AsyncIOMotorClient = Depends(get_database)):
    messages = await get_messages_by_id(id, db, limit, from_time, to_time)
    db_messages = Messages(messages=messages).messages

    json_users = []
    for i in db_messages:
        json_users.append(i.dict())

    return JSONResponse(jsonable_encoder(json_users)) # Response(json_users, media_type="application/json")
