from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import Runbook, Evidence
from app.schemas.schemas import RunbookOut, RunbookGenerateRequest, SearchResponse, EvidenceGraph
from app.services.runbook_generator import RunbookGenerator
from app.services.evidence_linker import EvidenceLinker
from app.services.rag_search import RAGSearchService

router = APIRouter(prefix="/runbooks")

@router.post("/generate", response_model=RunbookOut)
def generate_runbook(req: RunbookGenerateRequest, db: Session = Depends(get_db)):
    """
    Generates structured runbook from linked evidence.
    Distinguishes FACTS, INFERENCES, and RECOMMENDATIONS.
    Evaluates risk and determines approval requirement.
    """
    if not req.incident_id and not req.pr_id:
        raise HTTPException(status_code=400, detail="Must provide either incident_id or pr_id")
    
    runbook = RunbookGenerator.generate_runbook(
        db,
        incident_id=req.incident_id,
        pr_id=req.pr_id,
        force_demo_mode=req.force_demo_mode
    )
    
    # Attach evidence graph
    graph = EvidenceLinker.build_evidence_graph(db, incident_id=runbook.incident_id, pr_id=runbook.pr_id)
    out = RunbookOut.model_validate(runbook)
    out.evidence_graph = EvidenceGraph.model_validate(graph)
    return out

@router.get("/search", response_model=SearchResponse)
def search_runbooks(
    q: str = Query("", description="Search term, e.g. 'tax calculation', 'INC-052', 'RULE-TAX-104'"),
    limit: int = 15,
    db: Session = Depends(get_db)
):
    """
    Hybrid semantic & keyword search prioritizing VERIFIED runbooks.
    """
    results = RAGSearchService.search(db, query=q, limit=limit)
    response_items = []
    for r in results:
        rb = r["runbook"]
        graph = EvidenceLinker.build_evidence_graph(db, incident_id=rb.incident_id, pr_id=rb.pr_id)
        rb_out = RunbookOut.model_validate(rb)
        rb_out.evidence_graph = EvidenceGraph.model_validate(graph)
        response_items.append({
            "runbook": rb_out,
            "match_score": r["match_score"],
            "matched_by": r["matched_by"],
            "evidence_status": r["evidence_status"]
        })

    return {
        "query": q,
        "total_results": len(response_items),
        "results": response_items
    }

@router.get("", response_model=List[RunbookOut])
def list_runbooks(
    status: Optional[str] = None,
    risk: Optional[str] = None,
    module: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(Runbook)
    if status:
        query = query.filter(Runbook.status == status)
    if risk:
        query = query.filter(Runbook.risk_level == risk)
    if module:
        query = query.filter(Runbook.affected_module == module)
    
    runbooks = query.order_by(Runbook.created_at.desc()).limit(limit).all()
    output = []
    for rb in runbooks:
        graph = EvidenceLinker.build_evidence_graph(db, incident_id=rb.incident_id, pr_id=rb.pr_id)
        rb_out = RunbookOut.model_validate(rb)
        rb_out.evidence_graph = EvidenceGraph.model_validate(graph)
        output.append(rb_out)
    return output

@router.get("/{runbook_id}", response_model=RunbookOut)
def get_runbook(runbook_id: str, db: Session = Depends(get_db)):
    rb = db.query(Runbook).filter(Runbook.runbook_id == runbook_id).first()
    if not rb:
        raise HTTPException(status_code=404, detail=f"Runbook {runbook_id} not found")
    
    graph = EvidenceLinker.build_evidence_graph(db, incident_id=rb.incident_id, pr_id=rb.pr_id)
    rb_out = RunbookOut.model_validate(rb)
    rb_out.evidence_graph = EvidenceGraph.model_validate(graph)
    return rb_out
