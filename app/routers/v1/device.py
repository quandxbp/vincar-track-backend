from fastapi import FastAPI, Body, HTTPException, status, APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response, JSONResponse

from app import config
from app.schemas.device import *

import app.main as main

global_settings = config.get_settings()
DEVICES_COLLECTION = "devices"

router = APIRouter()

@router.post("/", response_description="Add new device", response_model=Device)
async def create_device(device: Device = Body(...)):
    device = jsonable_encoder(device)
    new_device = await main.app.state.mongo_collections[DEVICES_COLLECTION].insert_one(device)
    created_device = await main.app.state.mongo_collections[DEVICES_COLLECTION].find_one({"_id": new_device.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_device)


@router.get("/", response_description="List all devices", response_model=List[Device])
async def list_devices():
    devices = await main.app.state.mongo_collections[DEVICES_COLLECTION].find().to_list(1000)
    return devices


@router.get("/{id}", response_description="Get a single device", response_model=Device)
async def show_device(id: str):
    if (device := await main.app.state.mongo_collections[DEVICES_COLLECTION].find_one({"_id": id})) is not None:
        return device

    raise HTTPException(status_code=404, detail=f"device {id} not found")


@router.put("/{id}", response_description="Update a device", response_model=Device)
async def update_device(id: str, device: UpdateDevice = Body(...)):
    device = {k: v for k, v in device.dict().items() if v is not None}

    if len(device) >= 1:
        update_result = await main.app.state.mongo_collections[DEVICES_COLLECTION].update_one({"_id": id}, {"$set": device})

        if update_result.modified_count == 1:
            if (
                updated_device := await main.app.state.mongo_collections[DEVICES_COLLECTION].find_one({"_id": id})
            ) is not None:
                return updated_device

    if (existing_device := await main.app.state.mongo_collections[DEVICES_COLLECTION].find_one({"_id": id})) is not None:
        return existing_device

    raise HTTPException(status_code=404, detail=f"device {id} not found")


@router.delete("/{id}", response_description="Delete a device")
async def delete_device(id: str):
    delete_result = await main.app.state.mongo_collections[DEVICES_COLLECTION].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"device {id} not found")
