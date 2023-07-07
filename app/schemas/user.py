from bson import ObjectId
from pydantic import BaseModel, Field
from app.schemas.py_object import PyObjectId
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: Optional[str] = Field(...)
    # name: Optional[str] = Field(...)
    # email: Optional[str] = Field(...)
    # address: Optional[str] = Field(...)
    devices: Optional[List[str]] = Field(default=[], alias="devices")
    createdDate: datetime = Field(default_factory=datetime.utcnow)
    writeDate: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UpdateUser(BaseModel):
    name: Optional[str]
    email: Optional[str]
    address: Optional[str]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UpdateUserDevice(BaseModel):
    device_id: str
    is_add: bool

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ResponseUser(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: Optional[str]
    name: Optional[str]
    email: Optional[str]
    address: Optional[str]
    devices: Optional[List[str]]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str
    password: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserInDB(User):
    hashed_password: str