import uuid
import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import Runbook, Approval, OverrideHistory
from app.schemas.schemas import ApprovalRequest, OverrideRequest, OverrideHistoryOut, RunbookOut, EvidenceGraph
from app.services.evidence_linker import EvidenceLinker

router = APIRouter(prefix="/runbooks")

@router.post("/{runbook_id}/approve", response_model=RunbookOut)
def approve_runbook(
    runbook_id: str,
    approval_req: ApprovalRequest,
    db: Session = Depends(get_db)
):
    """
    Approve a pending high-risk runbook (PRD §14).
    Transitions status to VERIFIED or APPROVED.
    """
    rb = db.query(Runbook).filter(Runbook.runbook_id == runbook_id).first()
    if not rb:
        raise HTTPException(status_code=404, detail=f"Runbook {runbook_id} not found")

    approval = Approval(
        approval_id=f"APP-{uuid.uuid4().hex[:6].upper()}",
        runbook_id=runbook_id,
        decision="APPROVED",
        decided_by=approval_req.decided_by,
        reason=approval_req.reason or "Human engineer verified fix and safety bounds.",
        potential_impact=approval_req.potential_impact or f"Production fix approved for module {rb.affected_module}.",
        created_at=datetime.datetime.utcnow()
    )
    db.add(approval)

    rb.status = "VERIFIED"
    rb.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(rb)

    graph = EvidenceLinker.build_evidence_graph(db, incident_id=rb.incident_id, pr_id=rb.pr_id)
    out = RunbookOut.model_validate(rb)
    out.evidence_graph = EvidenceGraph.model_validate(graph)
    return out

@router.post("/{runbook_id}/reject", response_model=RunbookOut)
def reject_runbook(
    runbook_id: str,
    req: ApprovalRequest,
    db: Session = Depends(get_db)
):
    """
    Rejects a runbook. Rejection reason is mandatory per PRD §14.
    """
    if not req.reason or not req.reason.strip():
        raise HTTPException(status_code=400, detail="Rejection reason is strictly mandatory (PRD §14).")

    rb = db.query(Runbook).filter(Runbook.runbook_id == runbook_id).first()
    if not rb:
        raise HTTPException(status_code=404, detail=f"Runbook {runbook_id} not found")

    approval = Approval(
        approval_id=f"REJ-{uuid.uuid4().hex[:6].upper()}",
        runbook_id=runbook_id,
        decision="REJECTED",
        decided_by=req.decided_by,
        reason=req.reason,
        potential_impact=req.potential_impact or "Rejected due to safety constraints or insufficient verification.",
        created_at=datetime.datetime.utcnow()
    )
    db.add(approval)

    # Store audit history
    override_entry = OverrideHistory(
        runbook_id=runbook_id,
        user=req.decided_by,
        reason=req.reason,
        timestamp=datetime.datetime.utcnow(),
        previous_recommendation=str(rb.recommendations[0] if rb.recommendations else "Standard fix"),
        final_decision="REJECTED"
    )
    db.add(override_entry)

    rb.status = "REJECTED"
    rb.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(rb)

    graph = EvidenceLinker.build_evidence_graph(db, incident_id=rb.incident_id, pr_id=rb.pr_id)
    out = RunbookOut.model_validate(rb)
    out.evidence_graph = EvidenceGraph.model_validate(graph)
    return out

@router.post("/{runbook_id}/override", response_model=RunbookOut)
def override_runbook(
    runbook_id: str,
    override_req: OverrideRequest,
    db: Session = Depends(get_db)
):
    """
    Overrides or modifies runbook recommendations.
    Mandatory reason captured and logged into OverrideHistory (PRD §14).
    """
    if not override_req.reason or not override_req.reason.strip():
        raise HTTPException(status_code=400, detail="Override reason is strictly mandatory (PRD §14).")

    rb = db.query(Runbook).filter(Runbook.runbook_id == runbook_id).first()
    if not rb:
        raise HTTPException(status_code=404, detail=f"Runbook {runbook_id} not found")

    # Record in Override History table
    override_entry = OverrideHistory(
        runbook_id=runbook_id,
        user=override_req.user,
        reason=override_req.reason,
        timestamp=datetime.datetime.utcnow(),
        previous_recommendation=str(rb.recommendations[0] if rb.recommendations else "Standard fix"),
        final_decision=override_req.final_decision
    )
    db.add(override_entry)

    approval = Approval(
        approval_id=f"OVR-{uuid.uuid4().hex[:6].upper()}",
        runbook_id=runbook_id,
        decision="OVERRIDDEN",
        decided_by=override_req.user,
        reason=override_req.reason,
        potential_impact=f"Manual override executed by {override_req.user}.",
        created_at=datetime.datetime.utcnow()
    )
    db.add(approval)

    if override_req.modified_procedure:
        rb.fix_procedure = override_req.modified_procedure

    rb.status = "OVERRIDDEN"
    rb.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(rb)

    graph = EvidenceLinker.build_evidence_graph(db, incident_id=rb.incident_id, pr_id=rb.pr_id)
    out = RunbookOut.model_validate(rb)
    out.evidence_graph = EvidenceGraph.model_validate(graph)
    return out

@router.get("/{runbook_id}/overrides", response_model=List[OverrideHistoryOut])
def get_override_history(runbook_id: str, db: Session = Depends(get_db)):
    return db.query(OverrideHistory).filter(OverrideHistory.runbook_id == runbook_id).order_by(OverrideHistory.timestamp.desc()).all()
