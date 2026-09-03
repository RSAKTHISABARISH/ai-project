import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config import settings
from app.database.session import get_db
from app.data.synthetic_generator import seed_database
from app.schemas.schemas import HealthResponse, RunbookOut, EvidenceGraph
from app.services.runbook_generator import RunbookGenerator
from app.services.evidence_linker import EvidenceLinker
from app.models.models import Runbook

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health_check():
    """
    Health check declaring whether running in AI-Assisted Mode or Deterministic Demo Mode (PRD §5).
    """
    mode_label = "AI-Assisted Mode (Gemini API Active)" if settings.has_llm_key else "Deterministic / Demo Mode (Offline Fallback Active)"
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "mode": mode_label,
        "has_llm_key": settings.has_llm_key,
        "database": "SQLite (WAL Mode) - Ready for PostgreSQL",
        "timestamp": datetime.datetime.utcnow()
    }

@router.post("/demo/seed")
def seed_data(force_reset: bool = False, db: Session = Depends(get_db)):
    """
    Seeds comprehensive synthetic ERP datasets (30+ incidents, PRs, diffs, reviews, 100+ events).
    """
    counts = seed_database(db, force_reset=force_reset)
    return {
        "status": "SUCCESS",
        "message": "Synthetic ERP knowledge datasets successfully seeded.",
        "counts": counts
    }

@router.post("/demo/scenario-inc052", response_model=RunbookOut)
def load_scenario_inc052(db: Session = Depends(get_db)):
    """
    Loads and generates the primary showcase scenario: INC-052 / PR-142 (PRD §27).
    """
    # Ensure database is seeded
    seed_database(db, force_reset=False)
    
    # Check if runbook exists, otherwise generate
    rb = db.query(Runbook).filter(Runbook.incident_id == "INC-052").first()
    if not rb:
        rb = RunbookGenerator.generate_runbook(db, incident_id="INC-052")
    
    graph = EvidenceLinker.build_evidence_graph(db, incident_id="INC-052", pr_id="PR-142")
    out = RunbookOut.model_validate(rb)
    out.evidence_graph = EvidenceGraph.model_validate(graph)
    return out
