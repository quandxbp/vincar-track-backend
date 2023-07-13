from fastapi import FastAPI, Body, HTTPException, status, APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response, JSONResponse

from app import config
from app.schemas.license import *

import app.main as main

from bson import ObjectId

global_settings = config.get_settings()
LICENSE_COLLECTION = "license"

router = APIRouter()


@router.get("/", response_description="List all licenses", response_model=List[License])
async def list_licenses():
    licenses = await main.app.state.mongo_collections[LICENSE_COLLECTION].find().to_list(1000)
    return licenses


@router.post("/", response_description="Auto generate license")
async def create_license(data: LicenseCreate = Body(...)):
    created_license = await main.app.state.mongo_collections[LICENSE_COLLECTION].insert_one(jsonable_encoder(data))
    if (existing_license := await main.app.state.mongo_collections[LICENSE_COLLECTION].find_one(
            {"_id": created_license.inserted_id})) is not None:
        main.app.state.logger.info(existing_license)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=existing_license)


@router.get("/{code}", response_description="Get a single license", response_model=License)
async def get_license(code: str):
    if (l := await main.app.state.mongo_collections[LICENSE_COLLECTION].find_one({"code": code})) is not None:
        return l

    raise HTTPException(status_code=404, detail=f"License {code} not found")


@router.get("/by-user/{username}", response_description="Get a single license by username", response_model=License)
async def get_license_by_username(username: str):
    if (license_data := await main.app.state.mongo_collections[LICENSE_COLLECTION].find_one({"username": username})) is not None:
        return license_data

    raise HTTPException(status_code=404, detail=f"Username {username} not found")


@router.put("/{code}", response_description="Update a license")
async def update_license(code: str, data: LicenseUpdate = Body(...)):
    if (existing_license := await main.app.state.mongo_collections[LICENSE_COLLECTION].find_one({"code": code})) is not None:
        if existing_license.get("username"):
            return JSONResponse(status_code=status.HTTP_200_OK, content={"code": code, "is_exist": True})
        else:
            license_data = {k: v for k, v in data.dict().items() if v is not None}
            update_result = await main.app.state.mongo_collections[LICENSE_COLLECTION].update_one({"code": code},
                                                                                                  {"$set": license_data})
            return JSONResponse(status_code=status.HTTP_200_OK, content={"code": code, "is_exist": False})
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"License {code} not found")


@router.put("/reset/{code}", response_description="Reset a license")
async def reset_license(code: str):
    update_result = await main.app.state.mongo_collections[LICENSE_COLLECTION].update_one({"code": code},
                                                                                          {"$set": {"username": None}})
    if (existing_license := await main.app.state.mongo_collections[LICENSE_COLLECTION].find_one({"code": code})) is not None:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"success": True})
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"License {code} not found")


# @router.delete("/", response_description="Delete All")
# async def delete_all_license():
#     result = await main.app.state.mongo_collections[LICENSE_COLLECTION].delete_many({})
#     deleted_count = result.deleted_count
#
#     if deleted_count == 0:
#         raise HTTPException(status_code=404, detail="No documents found to delete")
#
#     return JSONResponse(status_code=200, content={
#         "message": f"Deleted {deleted_count} document(s) from the `{LICENSE_COLLECTION}` collection"})
