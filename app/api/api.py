from fastapi import APIRouter

from .endpoints.user import router as user_router
from .endpoints.authenticaion import router as auth_router
from .endpoints.devices import router as device_router
from .endpoints.messages import router as messages_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(user_router)
router.include_router(device_router)
router.include_router(messages_router)