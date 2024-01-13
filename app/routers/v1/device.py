from fastapi import FastAPI, Body, HTTPException, status, APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response, JSONResponse

from app import config
from app.schemas.device import *

import app.main as main

from bson import ObjectId

global_settings = config.get_settings()
DEVICES_COLLECTION = "devices"

PRIVATE_TOKEN = "Hungvuong12."

router = APIRouter()


@router.post("/", response_description="Add new device")
async def create_device(device: CreateDevice = Body(...)):
    existed_device = await main.app.state.mongo_collections[DEVICES_COLLECTION].find_one({"uuid": device.uuid})
    if existed_device:
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"_id": str(existed_device.get("_id"))})
    if not device.uuid:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"error": "Invalid content"})
    device = jsonable_encoder(device)
    new_device = await main.app.state.mongo_collections[DEVICES_COLLECTION].insert_one(device)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"_id": str(new_device.inserted_id)})


@router.get("/", response_description="List all devices", response_model=List[Device])
async def list_devices(page: int = 1, limit: int = 10):
    skip = (page - 1) * limit
    devices = await main.app.state.mongo_collections[DEVICES_COLLECTION].find().skip(skip).limit(limit).to_list(1000)
    return devices


@router.get("/{uuid}", response_description="Get a single device", response_model=Device)
async def show_device(uuid: str):
    if (device := await main.app.state.mongo_collections[DEVICES_COLLECTION].find_one({"uuid": uuid})) is not None:
        try:
            if device.get("writeDate"):
                device["isAlive"] = (datetime.utcnow() - device["writeDate"]) <= timedelta(minutes=1)
        except Exception as err:
            print(f"ERROR: ID {uuid} with writing isAlive: {err}")

        try:
            if device.get("writeDate"):
                device["writeDate"] = device["writeDate"] + timedelta(hours=7)
        except Exception as err:
            print(f"ERROR: ID {uuid} with writing writeDate: {err}")
        return device

    raise HTTPException(status_code=404, detail=f"device {uuid} not found")


@router.put("/{uuid}", response_description="Update a device")
async def update_device(uuid: str, device: UpdateDevice = Body(...)):
    if (found_device := await main.app.state.mongo_collections[DEVICES_COLLECTION].find_one({"uuid": uuid})) is not None:

        device = {k: v for k, v in device.dict().items() if v is not None}

        if len(found_device) >= 1:
            update_result = await main.app.state.mongo_collections[DEVICES_COLLECTION].update_one({"uuid": uuid},
                                                                                                  {"$set": device})

            if update_result.modified_count == 1:
                return JSONResponse(status_code=status.HTTP_200_OK, content={"uuid": uuid})
    else:
        device = jsonable_encoder(device)
        new_device = await main.app.state.mongo_collections[DEVICES_COLLECTION].insert_one(device)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"_id": str(new_device.inserted_id)})


@router.delete("/{uuid}", response_description="Delete a device")
async def delete_device(uuid: str):
    delete_result = await main.app.state.mongo_collections[DEVICES_COLLECTION].delete_one({"$or": [
        {"uuid": uuid},
        {"_id": uuid},
        {"_id": ObjectId(uuid)}]})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"device {uuid} not found")


@router.delete("/", response_description="Delete all issued devices")
async def delete_issue_devices():
    # if token == PRIVATE_TOKEN:
    delete_result = await main.app.state.mongo_collections[DEVICES_COLLECTION].delete_many({"uuid": None})

    if delete_result.deleted_count > 0:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    # else:
    #     return Response(status_code=status.HTTP_204_NO_CONTENT, detail=f"Deleting nothing")

    raise HTTPException(status_code=404, detail=f"Error when deleting error devices!")
