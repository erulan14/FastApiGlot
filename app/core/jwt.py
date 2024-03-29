from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends, Header, Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import PyJWTError
from starlette.exceptions import HTTPException
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from ..crud.user import get_user
from ..db.mongodb import AsyncIOMotorClient, get_database
from ..models.token import TokenPayload
from ..models.user import User

import time

from .config import JWT_TOKEN_PREFIX, SECRET_KEY

ALGORITHM = "HS256"
access_token_jwt_subject = "access"


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == JWT_TOKEN_PREFIX:
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    @staticmethod
    def verify_jwt(jw_token: str) -> bool:
        isTokenValid: bool = False
        try:
            payload = decodeJWT(token=jw_token)
        except:
            payload = None

        if payload:
            isTokenValid = True

        return isTokenValid


# def _get_authorization_token(authorization: str = Header(...)):
#     token_prefix, token = authorization.split(" ")
#     if token_prefix != JWT_TOKEN_PREFIX:
#         raise HTTPException(
#             status_code=HTTP_403_FORBIDDEN, detail="Invalid authorization type"
#         )
#
#     return token


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, str(SECRET_KEY), algorithms=[ALGORITHM])
        return decoded_token if decoded_token["exp"] >= time.time() else None
    except:
        return {}


async def _get_current_user(
    db: AsyncIOMotorClient = Depends(get_database), token: str = Depends(JWTBearer()) # Depends(_get_authorization_token)
) -> User:
    try:
        payload = jwt.decode(token, str(SECRET_KEY), algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except PyJWTError:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )

    dbuser = await get_user(db, token_data.username)
    if not dbuser:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")

    user = User(**dbuser.dict(), token=token)
    return user


# def _get_authorization_token_optional(authorization: str = Header(None)):
#     if authorization:
#         return _get_authorization_token(authorization)
#     return ""


# async def _get_current_user_optional(
#     db: AsyncIOMotorClient = Depends(get_database),
#     token: str = Depends(_get_authorization_token_optional),
# ) -> Optional[User]:
#     if token:
#         return await _get_current_user(db, token)
#
#     return None


def get_current_user_authorizer(*, required: bool = True):
    if required:
        return _get_current_user
    #else:
        #return _get_current_user_optional


def create_access_token(*, data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "sub": access_token_jwt_subject})
    encoded_jwt = jwt.encode(to_encode, str(SECRET_KEY), algorithm=ALGORITHM)
    return encoded_jwt