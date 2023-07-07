from bson import ObjectId
from bson.errors import InvalidId
from pydantic import BaseModel, Field
from app.schemas.py_object import PyObjectId
from typing import Optional, List
from datetime import datetime


class Device(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    uuid: Optional[str] = Field(...)
    licensePlates: Optional[str] = Field(...)
    latitude: Optional[float] = Field(...)
    longitude: Optional[float] = Field(...)
    createdDate: datetime = Field(default_factory=datetime.utcnow)
    writeDate: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UpdateDevice(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    uuid: Optional[str]
    licensePlates: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    writeDate: Optional[datetime]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class DeviceResponse(Device):
    id: PyObjectId = Field(...)
