from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ============ AUTH SCHEMAS ============

class UserSignup(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    phone: Optional[str] = None
    password: str = Field(..., min_length=6)
    role: str = "citizen"

    # Optional role-specific fields
    department: Optional[str] = None
    ward: Optional[str] = None
    district: Optional[str] = None
    constituency: Optional[str] = None
    parliamentary_constituency: Optional[str] = None
    zone: Optional[str] = None

    # Required for high-level roles
    invite_code: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    role: str
    department: Optional[str] = None
    ward: Optional[str] = None
    district: Optional[str] = None
    constituency: Optional[str] = None
    parliamentary_constituency: Optional[str] = None
    zone: Optional[str] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ============ REPORT SCHEMAS ============

class ReportOut(BaseModel):
    id: str
    category: str
    severity: str
    confidence: float
    latitude: float
    longitude: float
    image_url: str
    description: Optional[str] = ""
    status: str
    department: Optional[str] = None
    ward: Optional[str] = None
    district: Optional[str] = None
    assigned_to: Optional[int] = None
    reported_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StatusUpdate(BaseModel):
    status: str
    assigned_to: Optional[int] = None