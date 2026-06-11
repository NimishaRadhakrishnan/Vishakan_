from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from backend.app.models.farmer import UserRole

class FarmerBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, examples=["Ramesh Kumar"])
    mobile: str = Field(..., pattern=r"^\+?[0-9]{10,15}$", examples=["9876543210"])
    district: Optional[str] = Field(None, examples=["Coimbatore"])
    state: Optional[str] = Field(None, examples=["Tamil Nadu"])
    language: str = Field("English", examples=["Tamil"])
    role: UserRole = Field(default=UserRole.FARMER)

class FarmerCreate(FarmerBase):
    password: str = Field(..., min_length=6, examples=["secretpass"])

class FarmerLogin(BaseModel):
    mobile: str = Field(..., examples=["9876543210"])
    password: str = Field(..., examples=["secretpass"])

class FarmerResponse(BaseModel):
    id: int
    name: str
    mobile: str
    role: UserRole
    district: Optional[str] = None
    state: Optional[str] = None
    language: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class TokenData(BaseModel):
    mobile: Optional[str] = None
    role: Optional[str] = None
