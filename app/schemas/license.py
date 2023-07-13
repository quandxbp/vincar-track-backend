from bson import ObjectId
from pydantic import BaseModel, Field
from app.schemas.py_object import PyObjectId
from typing import Optional, List
from datetime import datetime, date

from app.services.license import *\


class License(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    code: Optional[str]
    username: Optional[str]
    startDate: Optional[datetime]
    createdDate: Optional[datetime]
    writeDate: Optional[datetime]
    lifetime: Optional[int]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class LicenseCreate(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    code: Optional[str] = Field(default_factory=lambda: generate_license_code())
    createdDate: datetime = Field(default_factory=datetime.utcnow)
    lifetime: Optional[int] = Field(default=365)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class LicenseUpdate(BaseModel):
    username: Optional[str]
    startDate: datetime
    writeDate: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
