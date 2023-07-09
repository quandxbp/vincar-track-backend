from fastapi import FastAPI, Body, HTTPException, status, APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response, JSONResponse

from app import config
from app.schemas.device import *

import app.main as main

from bson import ObjectId

global_settings = config.get_settings()
DEVICES_COLLECTION = "devices"

router = APIRouter()


@router.post("/", response_description="Add new device")
async def create_device(device: CreateDevice = Body(...)):
    existed_device = await main.app.state.mongo_collections[DEVICES_COLLECTION].find_one({"uuid": device.uuid})
    if existed_device:
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"_id": existed_device.id})
    device = jsonable_encoder(device)
    new_device = await main.app.state.mongo_collections[DEVICES_COLLECTION].insert_one(device)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"_id": str(new_device.inserted_id)})


@router.get("/", response_description="List all devices", response_model=List[Device])
async def list_devices():
    devices = await main.app.state.mongo_collections[DEVICES_COLLECTION].find().to_list(1000)
    return devices


@router.get("/{device_id}", response_description="Get a single device", response_model=Device)
async def show_device(device_id: str):
    if (device := await main.app.state.mongo_collections[DEVICES_COLLECTION].find_one({"_id": device_id})) is not None:
        return device

    raise HTTPException(status_code=404, detail=f"device {device_id} not found")


@router.put("/{device_id}", response_description="Update a device")
async def update_device(device_id: str, device: UpdateDevice = Body(...)):
    device = {k: v for k, v in device.dict().items() if v is not None}

    if len(device) >= 1:
        update_result = await main.app.state.mongo_collections[DEVICES_COLLECTION].update_one({"_id": device_id},
                                                                                              {"$set": device})

        if update_result.modified_count == 1:
            JSONResponse(status_code=status.HTTP_200_OK, content={"_id": device_id})

    if (existing_device := await main.app.state.mongo_collections[DEVICES_COLLECTION].find_one({"_id": device_id})) is not None:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"_id": device_id})

    raise HTTPException(status_code=404, detail=f"device {device_id} not found")


@router.delete("/{device_id}", response_description="Delete a device")
async def delete_device(device_id: str):
    delete_result = await main.app.state.mongo_collections[DEVICES_COLLECTION].delete_one({"_id": {"$in": [device_id, ObjectId(device_id)]}})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"device {device_id} not found")
