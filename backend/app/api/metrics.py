from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import BusinessRule
from app.schemas.schemas import MetricsSummary, BusinessRuleOut
from app.services.experiment_service import ExperimentService

router = APIRouter()

@router.get("/metrics", response_model=MetricsSummary)
def get_system_metrics(db: Session = Depends(get_db)):
    """
    Returns KPIs, measured vs baseline fix times, time reduction %,
    and error category taxonomy (PRD §2, §16, §19, §20).
    """
    return ExperimentService.get_metrics_summary(db)

@router.get("/business-rules", response_model=List[BusinessRuleOut])
def list_business_rules(db: Session = Depends(get_db)):
    """
    Lists ERP business rules with dependencies.
    """
    return db.query(BusinessRule).all()
