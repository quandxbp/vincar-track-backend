from fastapi import FastAPI, Body, HTTPException, status, APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response, JSONResponse
from passlib.context import CryptContext

from app import config
from app.schemas.user import *

import app.main as main

from bson import ObjectId

global_settings = config.get_settings()
USERS_COLLECTION = "users"

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


@router.get("/", response_description="List all users", response_model=List[ResponseUser])
async def list_users():
    users = await main.app.state.mongo_collections[USERS_COLLECTION].find().to_list(1000)
    return users


@router.get("/{id}", response_description="Get a single device", response_model=UpdateUser)
async def show_user(id: str):
    if (user := await main.app.state.mongo_collections[USERS_COLLECTION].find_one({"_id": ObjectId(id)})) is not None:
        return user

    raise HTTPException(status_code=404, detail=f"device {id} not found")


@router.post("/", response_description="Add new user", status_code=201)
async def create_user(user: UserCreate = Body(...)):
    existed_user = await main.app.state.mongo_collections[USERS_COLLECTION].find_one({"username": user.username})
    if existed_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed_password = get_password_hash(user.password)
    user_dict = {"username": user.username, "hashed_password": hashed_password, "password": user.password}
    new_user = await main.app.state.mongo_collections[USERS_COLLECTION].insert_one(jsonable_encoder(user_dict))
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"id": str(new_user.inserted_id)})


@router.delete("/{user_id}", response_description="Delete a user")
async def delete_user(user_id: str):
    user_id = ObjectId(user_id)
    delete_result = await main.app.state.mongo_collections[USERS_COLLECTION].delete_one({"_id": user_id})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"user {user_id} not found")


@router.put("/{user_id}", response_description="Update a user", response_model=ResponseUser)
async def update_user(user_id: str, user: UpdateUser = Body(...)):
    user_id = ObjectId(user_id)
    user = {k: v for k, v in user.dict().items() if v is not None}

    if len(user) >= 1:
        update_result = await main.app.state.mongo_collections[USERS_COLLECTION].update_one({"_id": user_id}, {"$set": user})

        if update_result.modified_count == 1:
            if (
                updated_user := await main.app.state.mongo_collections[USERS_COLLECTION].find_one({"_id": user_id})
            ) is not None:
                return updated_user

    if (existing_user := await main.app.state.mongo_collections[USERS_COLLECTION].find_one({"_id": user_id})) is not None:
        return existing_user

    raise HTTPException(status_code=404, detail=f"user {user_id} not found")


@router.put("/device/{user_id}", response_description="Update a user's Device", response_model=ResponseUser)
async def update_device_user(user_id: str, data: UpdateUserDevice = Body(...)):
    user_id = ObjectId(user_id)
    data = {k: v for k, v in data.dict().items() if v is not None}

    if len(data) >= 1:
        user = await main.app.state.mongo_collections[USERS_COLLECTION].find_one({"_id": user_id})
        if user:
            device_id = data['device_id']
            devices = user.get('devices', [])
            if data['is_add']:
                devices.append(device_id)
            else:
                devices.remove(device_id)

            update_result = await main.app.state.mongo_collections[USERS_COLLECTION].update_one(
                {"_id": user_id},
                {"$set": {'devices': list(set(devices))}}
            )
            if update_result.modified_count == 1:
                if (
                    updated_user := await main.app.state.mongo_collections[USERS_COLLECTION].find_one(
                        {"_id": user_id})
                ) is not None:
                    return updated_user
        else:
            raise HTTPException(status_code=404, detail=f"Could not find user {user_id}")
    raise HTTPException(status_code=404, detail="Provided data is needed")
