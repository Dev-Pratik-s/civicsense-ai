from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from datetime import datetime
import uuid
import os
import shutil
import random

from database import Base, engine, get_db
from models import User, Report
from schemas import UserSignup, UserLogin, UserOut, Token, ReportOut, StatusUpdate
from auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, require_role, get_optional_user,
)
from roles import (
    ALL_ROLES, INVITE_CODES, OPEN_ROLES,
    ROLE_CITIZEN, ROLE_DEPT_HEAD, ROLE_LOCAL_PRESIDENT,
    ROLE_DISTRICT_PRESIDENT, ROLE_MLA, ROLE_MP,
    ROLE_SUPERVISOR, ROLE_WORKER, ROLE_SUPER_ADMIN,
    CATEGORY_TO_DEPARTMENT, DEPARTMENTS,
    CAN_UPDATE_STATUS, CAN_ASSIGN_WORKER, CAN_VIEW_PREDICTIONS,
    CAN_MANAGE_USERS, CAN_VIEW_ANALYTICS, get_dashboard,
)

# ============ INIT DB ============
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CivicSense AI API",
    description="Predictive City Problem Detection Platform | SIH 2026 · PS 26205",
    version="2.0.0"
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


# ============ AI MOCK ============
def detect_issue(image_path: str) -> dict:
    categories = ["pothole", "garbage", "waterlogging", "streetlight"]
    severities = ["Low", "Medium", "High"]
    return {
        "category": random.choice(categories),
        "severity": random.choice(severities),
        "confidence": round(random.uniform(0.75, 0.98), 2),
    }


# ============ ROOT ============
@app.get("/")
def root():
    return {
        "message": "CivicSense AI API v2 is running",
        "ps_id": "26205",
        "status": "active",
        "roles_supported": len(ALL_ROLES),
    }


# ============ META (Public) ============
@app.get("/meta")
def meta():
    """Public endpoint — returns available roles, departments, invite requirements."""
    return {
        "roles": ALL_ROLES,
        "open_roles": OPEN_ROLES,
        "invite_required_roles": list(INVITE_CODES.keys()),
        "departments": DEPARTMENTS,
    }


# ============================================================
#                    AUTH ENDPOINTS
# ============================================================

@app.post("/auth/signup", response_model=Token)
def signup(data: UserSignup, db: Session = Depends(get_db)):
    # Validate role
    if data.role not in ALL_ROLES:
        raise HTTPException(400, f"Invalid role. Must be one of: {ALL_ROLES}")

    # Check email uniqueness
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "Email already registered")

    # Invite code check for high-level roles
    if data.role in INVITE_CODES:
        if not data.invite_code:
            raise HTTPException(400, f"Invite code required for role '{data.role}'")
        if data.invite_code != INVITE_CODES[data.role]:
            raise HTTPException(400, "Invalid invite code")

    # Role-specific field validation
    if data.role in [ROLE_DEPT_HEAD, ROLE_WORKER] and not data.department:
        raise HTTPException(400, "Department is required for this role")
    if data.role in [ROLE_LOCAL_PRESIDENT, ROLE_WORKER] and not data.ward:
        raise HTTPException(400, "Ward is required for this role")
    if data.role == ROLE_DISTRICT_PRESIDENT and not data.district:
        raise HTTPException(400, "District is required for this role")
    if data.role == ROLE_MLA and not data.constituency:
        raise HTTPException(400, "Constituency is required for MLA")
    if data.role == ROLE_MP and not data.parliamentary_constituency:
        raise HTTPException(400, "Parliamentary constituency is required for MP")
    if data.role == ROLE_SUPERVISOR and not data.zone:
        raise HTTPException(400, "Zone is required for Supervisor")

    user = User(
        name=data.name,
        email=data.email,
        phone=data.phone,
        hashed_password=hash_password(data.password),
        role=data.role,
        department=data.department,
        ward=data.ward,
        district=data.district,
        constituency=data.constituency,
        parliamentary_constituency=data.parliamentary_constituency,
        zone=data.zone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.email, "role": user.role})
    return {"access_token": token, "token_type": "bearer", "user": user}


@app.post("/auth/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "Invalid email or password")

    token = create_access_token({"sub": user.email, "role": user.role})
    return {"access_token": token, "token_type": "bearer", "user": user}


@app.get("/auth/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "user": UserOut.model_validate(current_user),
        "dashboard": get_dashboard(current_user.role),
    }


# ============================================================
#                    REPORT ENDPOINTS
# ============================================================

def filter_reports_by_scope(query, user: User):
    """Apply role-based filtering to report queries."""
    role = user.role

    if role == ROLE_CITIZEN:
        return query.filter(Report.reported_by == user.id)

    if role == ROLE_WORKER:
        return query.filter(
            or_(
                Report.assigned_to == user.id,
                and_(
                    Report.department == user.department,
                    Report.status == "Pending",
                )
            )
        )

    if role == ROLE_DEPT_HEAD:
        return query.filter(Report.department == user.department)

    if role == ROLE_LOCAL_PRESIDENT:
        return query.filter(Report.ward == user.ward)

    if role == ROLE_SUPERVISOR:
        return query.filter(Report.ward == user.zone)

    if role == ROLE_DISTRICT_PRESIDENT:
        return query.filter(Report.district == user.district)

    if role == ROLE_MLA:
        return query.filter(Report.district == user.constituency)

    if role == ROLE_MP:
        # MP sees whole state (simplified — we return all)
        return query

    if role == ROLE_SUPER_ADMIN:
        return query

    return query.filter(Report.id == "___none___")  # empty


@app.post("/report", response_model=ReportOut)
async def create_report(
    file: UploadFile = File(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    description: str = Form(""),
    ward: str = Form(""),
    district: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_id = str(uuid.uuid4())
    ext = file.filename.split(".")[-1]
    filename = f"{file_id}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    ai_result = detect_issue(filepath)
    auto_dept = CATEGORY_TO_DEPARTMENT.get(ai_result["category"], "Roads & Infrastructure")

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
        department=auto_dept,
        ward=ward or current_user.ward,
        district=district or current_user.district,
        reported_by=current_user.id,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@app.get("/reports", response_model=List[ReportOut])
def get_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Report).order_by(Report.created_at.desc())
    query = filter_reports_by_scope(query, current_user)
    return query.all()


@app.get("/reports/{report_id}", response_model=ReportOut)
def get_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(404, "Report not found")
    return report


@app.get("/map-data")
def get_map_data(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Public map data (no auth needed)."""
    reports = db.query(Report).all()
    features = []
    for r in reports:
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [r.longitude, r.latitude]},
            "properties": {
                "id": r.id,
                "category": r.category,
                "severity": r.severity,
                "status": r.status,
                "confidence": r.confidence,
                "department": r.department,
            },
        })
    return {"type": "FeatureCollection", "features": features}


@app.put("/report/{report_id}/status")
def update_status(
    report_id: str,
    payload: StatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*CAN_UPDATE_STATUS)),
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(404, "Report not found")

    report.status = payload.status
    if payload.assigned_to and current_user.role in CAN_ASSIGN_WORKER:
        report.assigned_to = payload.assigned_to

    db.commit()
    db.refresh(report)
    return {"message": "Updated", "report": report}


# ============================================================
#                    PREDICTIONS
# ============================================================

@app.get("/predict")
def predict_hotspots(current_user: User = Depends(require_role(*CAN_VIEW_PREDICTIONS))):
    zones = [
        {"zone": "Ward 4", "risk": "High", "likely_issue": "Pothole", "department": "Roads & Infrastructure"},
        {"zone": "MG Road", "risk": "Medium", "likely_issue": "Waterlogging", "department": "Water Supply"},
        {"zone": "Station Area", "risk": "High", "likely_issue": "Garbage", "department": "Sanitation & Waste"},
    ]
    return {"predictions": zones}


# ============================================================
#                    ADMIN ENDPOINTS
# ============================================================

@app.get("/admin/users", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*CAN_MANAGE_USERS)),
):
    return db.query(User).all()


@app.get("/admin/stats")
def admin_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*CAN_VIEW_ANALYTICS)),
):
    total_reports = db.query(Report).count()
    pending = db.query(Report).filter(Report.status == "Pending").count()
    resolved = db.query(Report).filter(Report.status == "Resolved").count()

    by_dept = {}
    for dept in DEPARTMENTS:
        by_dept[dept] = db.query(Report).filter(Report.department == dept).count()

    response = {
        "total_reports": total_reports,
        "pending": pending,
        "resolved": resolved,
        "by_department": by_dept,
    }

    if current_user.role == ROLE_SUPER_ADMIN:
        response["total_users"] = db.query(User).count()
        response["roles_breakdown"] = {
            role: db.query(User).filter(User.role == role).count()
            for role in ALL_ROLES
        }
    return response