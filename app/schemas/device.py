from bson import ObjectId
from pydantic import BaseModel, Field
from app.schemas.py_object import PyObjectId
from typing import Optional, List
from datetime import datetime, timedelta


class Device(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    uuid: Optional[str] = Field(...)
    licensePlates: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    createdDate: Optional[datetime]
    writeDate: Optional[datetime]
    isAlive: Optional[bool] = Field(default=False)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class CreateDevice(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    uuid: Optional[str] = Field(...)
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
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class DeviceResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    licensePlates: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    writeDate: Optional[datetime]
    isAlive: Optional[bool] = Field(default=False)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}