from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="citizen")

    # Role-specific fields (nullable — only filled for relevant roles)
    department = Column(String, nullable=True)
    ward = Column(String, nullable=True)
    district = Column(String, nullable=True)
    constituency = Column(String, nullable=True)
    parliamentary_constituency = Column(String, nullable=True)
    zone = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, index=True)
    category = Column(String)
    severity = Column(String)
    confidence = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    image_url = Column(String)
    description = Column(Text)
    status = Column(String, default="Pending")
    department = Column(String, nullable=True)
    ward = Column(String, nullable=True)
    district = Column(String, nullable=True)
    assigned_to = Column(Integer, nullable=True)
    reported_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)