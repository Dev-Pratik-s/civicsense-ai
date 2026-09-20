"""
CivicSense AI — Role Hierarchy & Permissions
9 Roles with geographic + department-based access control
"""

# ============ ROLE CONSTANTS ============

ROLE_CITIZEN = "citizen"
ROLE_DEPT_HEAD = "dept_head"
ROLE_LOCAL_PRESIDENT = "local_president"
ROLE_DISTRICT_PRESIDENT = "district_president"
ROLE_MLA = "mla"
ROLE_MP = "mp"
ROLE_SUPERVISOR = "supervisor"
ROLE_WORKER = "worker"
ROLE_SUPER_ADMIN = "super_admin"

ALL_ROLES = [
    ROLE_CITIZEN,
    ROLE_DEPT_HEAD,
    ROLE_LOCAL_PRESIDENT,
    ROLE_DISTRICT_PRESIDENT,
    ROLE_MLA,
    ROLE_MP,
    ROLE_SUPERVISOR,
    ROLE_WORKER,
    ROLE_SUPER_ADMIN,
]

ROLE_LEVEL = {
    ROLE_CITIZEN: 1,
    ROLE_WORKER: 2,
    ROLE_DEPT_HEAD: 3,
    ROLE_LOCAL_PRESIDENT: 4,
    ROLE_SUPERVISOR: 5,
    ROLE_DISTRICT_PRESIDENT: 6,
    ROLE_MLA: 7,
    ROLE_MP: 8,
    ROLE_SUPER_ADMIN: 9,
}

INVITE_CODES = {
    ROLE_DISTRICT_PRESIDENT: "DIST2026",
    ROLE_MLA: "MLA2026",
    ROLE_MP: "MP2026",
    ROLE_SUPERVISOR: "SUP2026",
    ROLE_WORKER: "WORK2026",
    ROLE_SUPER_ADMIN: "ADMIN2026",
}

OPEN_ROLES = [
    ROLE_CITIZEN,
    ROLE_DEPT_HEAD,
    ROLE_LOCAL_PRESIDENT,
]

DEPARTMENTS = [
    "Roads & Infrastructure",
    "Water Supply",
    "Sanitation & Waste",
    "Electricity",
    "Traffic & Transport",
]

CATEGORY_TO_DEPARTMENT = {
    "pothole": "Roads & Infrastructure",
    "garbage": "Sanitation & Waste",
    "waterlogging": "Water Supply",
    "streetlight": "Electricity",
}


def get_report_scope(role: str, user) -> dict:
    if role == ROLE_CITIZEN:
        return {"scope": "own", "user_id": user.id}
    if role == ROLE_WORKER:
        return {"scope": "assigned_or_dept", "user_id": user.id, "department": user.department, "zone": user.zone}
    if role == ROLE_DEPT_HEAD:
        return {"scope": "department", "department": user.department}
    if role == ROLE_LOCAL_PRESIDENT:
        return {"scope": "ward", "ward": user.ward}
    if role == ROLE_SUPERVISOR:
        return {"scope": "zone", "zone": user.zone}
    if role == ROLE_DISTRICT_PRESIDENT:
        return {"scope": "district", "district": user.district}
    if role == ROLE_MLA:
        return {"scope": "constituency", "constituency": user.constituency}
    if role == ROLE_MP:
        return {"scope": "parliamentary", "parliamentary_constituency": user.parliamentary_constituency}
    if role == ROLE_SUPER_ADMIN:
        return {"scope": "all"}
    return {"scope": "none"}


CAN_UPDATE_STATUS = [
    ROLE_DEPT_HEAD,
    ROLE_SUPERVISOR,
    ROLE_WORKER,
    ROLE_SUPER_ADMIN,
]

CAN_ASSIGN_WORKER = [
    ROLE_DEPT_HEAD,
    ROLE_SUPERVISOR,
    ROLE_SUPER_ADMIN,
]

CAN_VIEW_PREDICTIONS = [
    ROLE_DEPT_HEAD,
    ROLE_LOCAL_PRESIDENT,
    ROLE_SUPERVISOR,
    ROLE_DISTRICT_PRESIDENT,
    ROLE_MLA,
    ROLE_MP,
    ROLE_SUPER_ADMIN,
]

CAN_MANAGE_USERS = [ROLE_SUPER_ADMIN]

CAN_VIEW_ANALYTICS = [
    ROLE_DEPT_HEAD,
    ROLE_LOCAL_PRESIDENT,
    ROLE_SUPERVISOR,
    ROLE_DISTRICT_PRESIDENT,
    ROLE_MLA,
    ROLE_MP,
    ROLE_SUPER_ADMIN,
]


def get_dashboard(role: str) -> str:
    if role == ROLE_CITIZEN:
        return "citizen"
    if role in [ROLE_MLA, ROLE_MP, ROLE_DISTRICT_PRESIDENT]:
        return "executive"
    if role == ROLE_SUPER_ADMIN:
        return "admin"
    return "authority"
