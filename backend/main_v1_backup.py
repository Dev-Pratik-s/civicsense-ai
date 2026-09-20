from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from datetime import datetime
import uuid
import os
import shutil
import random

app = FastAPI(
    title="CivicSense AI API",
    description="Predictive City Problem Detection Platform | SIH 2026",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

reports_db = []


class Report(BaseModel):
    id: str
    category: str
    severity: str
    confidence: float
    latitude: float
    longitude: float
    image_url: str
    description: str
    status: str
    created_at: str


def detect_issue(image_path: str) -> dict:
    categories = ["pothole", "garbage", "waterlogging", "streetlight"]
    severities = ["Low", "Medium", "High"]
    return {
        "category": random.choice(categories),
        "severity": random.choice(severities),
        "confidence": round(random.uniform(0.75, 0.98), 2)
    }


@app.get("/")
def root():
    return {
        "message": "CivicSense AI API is running",
        "ps_id": "26205",
        "status": "active"
    }


@app.post("/report", response_model=Report)
async def create_report(
    file: UploadFile = File(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    description: str = Form("")
):
    file_id = str(uuid.uuid4())
    ext = file.filename.split(".")[-1]
    filename = f"{file_id}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    ai_result = detect_issue(filepath)

    report = Report(
        id=file_id,
        category=ai_result["category"],
        severity=ai_result["severity"],
        confidence=ai_result["confidence"],
        latitude=latitude,
        longitude=longitude,
        image_url=f"/uploads/{filename}",
        description=description,
        status="Pending",
        created_at=datetime.now().isoformat()
    )

    reports_db.append(report.dict())
    return report


@app.get("/reports", response_model=List[Report])
def get_reports():
    return reports_db


@app.get("/map-data")
def get_map_data():
    features = []
    for r in reports_db:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [r["longitude"], r["latitude"]]
            },
            "properties": {
                "id": r["id"],
                "category": r["category"],
                "severity": r["severity"],
                "status": r["status"],
                "confidence": r["confidence"]
            }
        })
    return {"type": "FeatureCollection", "features": features}


@app.get("/predict")
def predict_hotspots():
    zones = [
        {"zone": "Sector 4", "risk": "High", "likely_issue": "Pothole"},
        {"zone": "MG Road", "risk": "Medium", "likely_issue": "Waterlogging"},
        {"zone": "Station Area", "risk": "High", "likely_issue": "Garbage"}
    ]
    return {"predictions": zones}