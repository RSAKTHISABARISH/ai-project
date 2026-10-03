import datetime
import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import Event, EventProcessingLog
from app.schemas.schemas import EventCreate, EventOut, EventProcessResult
from app.services.event_processor import EventProcessor

router = APIRouter(prefix="/events")

@router.post("", response_model=EventProcessResult)
def ingest_event(event_in: EventCreate, db: Session = Depends(get_db)):
    """
    Ingests an event with idempotent deduplication and state machine transition.
    """
    result = EventProcessor.process_event(db, event_in.model_dump())
    return result

@router.get("", response_model=List[EventOut])
def list_events(limit: int = 50, db: Session = Depends(get_db)):
    """
    Lists received events chronologically.
    """
    return db.query(Event).order_by(Event.received_at.desc()).limit(limit).all()

@router.get("/logs")
def list_event_logs(limit: int = 50, db: Session = Depends(get_db)):
    """
    Returns audit logs from event processing including idempotency checks.
    """
    return db.query(EventProcessingLog).order_by(EventProcessingLog.timestamp.desc()).limit(limit).all()

@router.post("/inject-duplicate")
def inject_duplicate_event(db: Session = Depends(get_db)):
    """
    Demonstrates Edge Case 1: Injects an identical event twice.
    Proves that the system records the event idempotently without duplicating knowledge or altering state.
    """
    dup_id = "EVT-DUP-TAX-999"
    now = datetime.datetime.utcnow()
    
    event_payload = {
        "event_id": dup_id,
        "event_type": "PR_APPROVED",
        "source": "github",
        "entity_id": "PR-142",
        "event_timestamp": now.isoformat(),
        "received_at": now.isoformat(),
        "payload": {"status": "MERGED", "note": "Duplicate simulation payload"},
        "version": 1
    }

    # First injection
    res1 = EventProcessor.process_event(db, event_payload)
    # Second injection (Duplicate)
    res2 = EventProcessor.process_event(db, event_payload)

    return {
        "status": "SUCCESS",
        "message": "Duplicate event injected and filtered via idempotency engine.",
        "first_attempt": res1,
        "second_attempt_duplicate_check": res2
    }

@router.post("/inject-delayed")
def inject_delayed_event(db: Session = Depends(get_db)):
    """
    Demonstrates Edge Case 2: Injects an event with an older timestamp arriving late.
    The system reconstructs the logical timeline using event_timestamp rather than received_at.
    """
    delayed_id = f"EVT-DELAYED-{uuid.uuid4().hex[:6].upper()}"
    simulated_event_time = datetime.datetime.utcnow() - datetime.timedelta(hours=6)
    
    event_payload = {
        "event_id": delayed_id,
        "event_type": "INCIDENT_RESOLVED",
        "source": "pagerduty",
        "entity_id": "INC-052",
        "event_timestamp": simulated_event_time.isoformat(),
        "payload": {"resolution": "Delayed webhook arrival after network restoration"},
        "version": 2
    }

    result = EventProcessor.process_event(db, event_payload)
    return {
        "status": "SUCCESS",
        "message": "Delayed event processed and positioned in logical timeline.",
        "logical_timestamp": simulated_event_time.isoformat(),
        "actual_received_at": datetime.datetime.utcnow().isoformat(),
        "result": result
    }

@router.post("/inject-out-of-order")
def inject_out_of_order_event(db: Session = Depends(get_db)):
    """
    Demonstrates Edge Case 3: Injects Review Approval BEFORE PR creation.
    The state machine queues the review event in PENDING_RECONCILIATION without corrupting state,
    and reconciles automatically when the PR is created.
    """
    test_pr_id = f"PR-OOO-{uuid.uuid4().hex[:4].upper()}"
    rev_event_id = f"EVT-OOO-REV-{uuid.uuid4().hex[:4].upper()}"
    pr_event_id = f"EVT-OOO-PR-{uuid.uuid4().hex[:4].upper()}"
    
    now = datetime.datetime.utcnow()

    # Step 1: Inject Reviewer Approval first (Out-of-order!)
    review_event = {
        "event_id": rev_event_id,
        "event_type": "REVIEW_APPROVED",
        "source": "github",
        "entity_id": test_pr_id,
        "event_timestamp": (now + datetime.timedelta(minutes=10)).isoformat(),
        "payload": {"reviewer": "staff.architect", "decision": "APPROVED"},
        "version": 1
    }
    step1_res = EventProcessor.process_event(db, review_event)

    # Step 2: Inject PR creation event later
    pr_event = {
        "event_id": pr_event_id,
        "event_type": "PR_CREATED",
        "source": "github",
        "entity_id": test_pr_id,
        "event_timestamp": now.isoformat(),
        "payload": {"pr_id": test_pr_id, "title": "Out of Order PR Demo"},
        "version": 1
    }
    step2_res = EventProcessor.process_event(db, pr_event)

    return {
        "status": "SUCCESS",
        "message": "Out-of-order sequence handled safely by state machine without state corruption.",
        "step_1_out_of_order_review": step1_res,
        "step_2_pr_arrived_and_reconciled": step2_res
    }
