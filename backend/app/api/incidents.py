from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import Incident
from app.schemas.schemas import IncidentCreate, IncidentOut

router = APIRouter(prefix="/incidents")

@router.post("", response_model=IncidentOut)
def create_incident(inc_in: IncidentCreate, db: Session = Depends(get_db)):
    existing = db.query(Incident).filter(Incident.incident_id == inc_in.incident_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Incident {inc_in.incident_id} already exists")
    inc = Incident(**inc_in.model_dump())
    db.add(inc)
    db.commit()
    db.refresh(inc)
    return inc

@router.get("", response_model=List[IncidentOut])
def list_incidents(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Incident).order_by(Incident.created_at.desc()).limit(limit).all()

@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return inc
