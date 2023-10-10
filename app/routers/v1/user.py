from fastapi import FastAPI, Body, HTTPException, status, APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response, JSONResponse
from passlib.context import CryptContext

from app import config
from app.schemas.user import *
from app.schemas.device import *

import app.main as main

from bson import ObjectId

global_settings = config.get_settings()
USERS_COLLECTION = "users"
DEVICES_COLLECTION = "devices"

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


@router.get("/", response_description="List all users", response_model=List[ResponseUser])
async def list_users(page: int = 1, limit: int = 10):
    skip = (page - 1) * limit
    users = await main.app.state.mongo_collections[USERS_COLLECTION].find().skip(skip).limit(limit).to_list(1000)
    return users


@router.get("/{username}", response_description="Get a single User", response_model=UpdateUser)
async def show_user(username: str):
    if (user := await main.app.state.mongo_collections[USERS_COLLECTION].find_one({"username": username})) is not None:
        return user

    raise HTTPException(status_code=404, detail=f"User {username} not found")


@router.post("/", response_description="Add new user", status_code=201)
async def create_user(user: UserCreate = Body(...)):
    existed_user = await main.app.state.mongo_collections[USERS_COLLECTION].find_one({"username": user.username})
    if existed_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    # hashed_password = get_password_hash(user.password)
    # user_dict = {"username": user.username, "hashed_password": hashed_password, "password": user.password}
    new_user = await main.app.state.mongo_collections[USERS_COLLECTION].insert_one(jsonable_encoder(user))
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"_id": str(new_user.inserted_id)})


@router.delete("/{user_id}", response_description="Delete a user")
async def delete_user(user_id: str):
    delete_result = await main.app.state.mongo_collections[USERS_COLLECTION].delete_one(
        {"_id": {"$in": [user_id, ObjectId(user_id)]}}
    )

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"user {user_id} not found")


@router.put("/{username}", response_description="Update a user", response_model=ResponseUser)
async def update_user(username: str, user: UpdateUser = Body(...)):
    user = {k: v for k, v in user.dict().items() if v is not None}

    if len(user) >= 1:
        update_result = await main.app.state.mongo_collections[USERS_COLLECTION].update_one({"username": username}, {"$set": user})

        if update_result.modified_count == 1:
            if (
                updated_user := await main.app.state.mongo_collections[USERS_COLLECTION].find_one({"username": username})
            ) is not None:
                return updated_user

    if (existing_user := await main.app.state.mongo_collections[USERS_COLLECTION].find_one({"username": username})) is not None:
        return existing_user

    raise HTTPException(status_code=404, detail=f"User {username} not found")


@router.get("/device/{username}",
            response_description="List all devices by username",
            response_model=List[DeviceResponse])
async def list_devices_by_user_id(username: str):
    if (user := await main.app.state.mongo_collections[USERS_COLLECTION].find_one({"username": username})) is not None:
        device_uuid_lst = user.get('devices', [])
        devices = await main.app.state.mongo_collections[DEVICES_COLLECTION].find(
            {"uuid": {"$in": device_uuid_lst}}
        ).to_list(length=None)
        for device in devices:
            if device["writeDate"] is not None:
                if isinstance(device["writeDate"], str):
                    device["writeDate"] = datetime.strptime(device["writeDate"], "%Y-%m-%dT%H:%M:%S.%f")
                device["isAlive"] = (datetime.utcnow() - device["writeDate"]) <= timedelta(minutes=1)
        return devices
    raise HTTPException(status_code=404, detail=f"User {username} not found")


@router.put("/device/{username}", response_description="Update a user's Device", response_model=ResponseUser)
async def update_user_device(username: str, data: UpdateUserDevice = Body(...)):
    data = {k: v for k, v in data.dict().items() if v is not None}

    if len(data) >= 1:
        user = await main.app.state.mongo_collections[USERS_COLLECTION].find_one({"username": username})
        if user:
            device_id = data['device_id']
            devices = user.get('devices', [])
            if data['is_add']:
                devices.append(device_id)
            else:
                devices.remove(device_id)

            update_result = await main.app.state.mongo_collections[USERS_COLLECTION].update_one(
                {"username": username},
                {"$set": {'devices': list(set(devices))}}
            )
            if update_result.modified_count == 1:
                if (
                    updated_user := await main.app.state.mongo_collections[USERS_COLLECTION].find_one(
                        {"username": username})
                ) is not None:
                    return updated_user
        else:
            raise HTTPException(status_code=404, detail=f"Could not find user {username}")
    raise HTTPException(status_code=404, detail="Provided data is needed")
