from datetime import timedelta
from fastapi import APIRouter, Body, Depends, Response
from starlette.exceptions import HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from ...core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from ...core.jwt import create_access_token
from ...crud.shortcuts import check_free_username_and_email
from ...crud.user import create_user, get_user_by_email, get_user_by_username
from ...db.mongodb import AsyncIOMotorClient, get_database
from ...models.user import User, UserInCreate, UserInLogin, UserInResponse
from ...core.jwt import JWTBearer

import json

router = APIRouter()


@router.post(
    "/users/login", response_model=User,
    tags=["authentication"]
)
async def login(
        user: UserInLogin, db:
        AsyncIOMotorClient =
        Depends(get_database)
):
    db_user = await get_user_by_username(db, user.username)
    if not db_user or not db_user.check_password(user.password):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )

    access_token_expires = timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    token = create_access_token(
        data={"username": db_user.username},
        expires_delta=access_token_expires
    )
    return Response(json.dumps(
        User(**db_user.dict(),
            token=token).dict()
    ), media_type="application/json")


@router.post(
    "/users",
    response_model=UserInResponse,
    tags=["authentication"],
    status_code=HTTP_201_CREATED,

)
async def register(
        user: UserInCreate = Body(..., embed=True),
        db: AsyncIOMotorClient = Depends(get_database)
):
    await check_free_username_and_email(db, user.username, user.email)

    async with await db.start_session() as s:
        async with s.start_transaction():
            db_user = await create_user(db, user)
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            token = create_access_token(
                data={"username": db_user.username}, expires_delta=access_token_expires
            )

            return Response(
                json.dumps(
                    User(
                        **db_user.dict(),
                        token=token).dict()
                ), media_type="application/json"
            ) # UserInResponse(user=User(**dbuser.dict(), token=token))