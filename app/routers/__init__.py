from fastapi import APIRouter

from app.routers.v1.device import router as device_api
from app.routers.v1.user import router as user_api

router = APIRouter()

router.include_router(device_api, prefix="/device", tags=["Devices"])
router.include_router(user_api, prefix="/user", tags=["Users"])
