from fastapi import APIRouter, Body, Depends, Response
import json

from ...core.jwt import get_current_user_authorizer, JWTBearer, _get_current_user
from ...crud.shortcuts import check_free_username_and_email
from ...crud.user import update_user, get_users, delete_user
from ...db.mongodb import AsyncIOMotorClient, get_database
from ...models.user import User, UserInResponse, UserInUpdate, Users
from ...core.utils import create_aliased_response

router = APIRouter()


@router.get("/users/", response_model=Users, tags=["users"], dependencies=[Depends(JWTBearer())])
async def get_users_list(db: AsyncIOMotorClient = Depends(get_database)):
    users = await get_users(db)
    db_users = Users(users = users).users
    json_users = []
    for i in db_users:
        json_users.append(i.dict())
    return Response(json.dumps(json_users), media_type="application/json")#create_aliased_response(db_users)


@router.get("/user", response_model=User, tags=["user"])
async def retrieve_current_user(user: User = Depends(get_current_user_authorizer())):
    print(user.dict())
    return Response(json.dumps([user.dict()]), media_type="application/json")


@router.put("/user", response_model=User, tags=["user"])
async def update_current_user(
    user: UserInUpdate = Body(..., embed=False),
    current_user: User = Depends(get_current_user_authorizer()),
    db: AsyncIOMotorClient = Depends(get_database),
):
    if user.username == current_user.username:
        user.username = None
    if user.email == current_user.email:
        user.email = None

    await check_free_username_and_email(db, user.username, user.email)

    db_user = await update_user(db, current_user.username, user)

    return Response(json.dumps(User(**db_user.dict(), token=current_user.token).dict()), media_type="application/json") # UserInResponse(user=User(**dbuser.dict(), token=current_user.token))


@router.delete("/users/{item_id}", response_model=User, tags=["users"], dependencies=[Depends(JWTBearer())])
async def delete_user_by_id(
    item_id: str | None = None,
    db: AsyncIOMotorClient = Depends(get_database),
):
    #print(id)
    if await delete_user(db, item_id):
        return Response(content="", status_code=201)
    return Response(content="", status_code=404)