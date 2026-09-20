# 🏙️ CivicSense AI
### Predictive City Problem Detection & Intelligent Civic Response Platform

**Smart India Hackathon 2026** · **Problem Statement ID: 26205**
**Theme:** Transportation & Logistics · **Category:** Software

---

## 🎯 Problem
Cities face growing pressure on resources, transport networks, and logistics infrastructure. Civic issues like potholes, garbage accumulation, waterlogging, and delayed response go unreported or unprioritized.

## 💡 Solution
CivicSense AI is an AI-powered platform that:
- 📸 Collects citizen reports with photo + GPS
- 🤖 Detects civic problems using AI
- 🎯 Classifies severity automatically
- 🗺️ Displays issues on a live city map
- ⚡ Alerts the right authority instantly

## 🏛️ 9-Role RBAC System
| # | Role | Scope |
|---|------|-------|
| 1 | Citizen | Own reports |
| 2 | Department Head | Department-wide |
| 3 | Local President | Ward-level |
| 4 | District President | District-wide |
| 5 | MLA | Constituency |
| 6 | MP | Parliamentary |
| 7 | Supervisor | Zone |
| 8 | Worker | Assigned tasks |
| 9 | Super Admin | Full system |

## 🛠️ Tech Stack
| Layer | Technology |
|-------|-----------|
| Frontend | React + Vite + Tailwind + Leaflet |
| Backend | FastAPI (Python) |
| Database | SQLite (SQLAlchemy) |
| Auth | JWT + bcrypt |
| AI/ML | YOLOv8 (planned) |
| Deploy | Vercel + Render |

## 🚀 Getting Started

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

→ API docs: http://127.0.0.1:8000/docs


