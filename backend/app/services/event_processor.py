import datetime
import uuid
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.models import Event, EventProcessingLog, Incident, PullRequest, Review, CodeDiff, Runbook
from app.services.rule_engine import RuleEngine

# State machine states
STATE_CREATED = "CREATED"
STATE_FIX_IDENTIFIED = "FIX_IDENTIFIED"
STATE_REVIEWED = "REVIEWED"
STATE_VERIFIED = "VERIFIED"
STATE_RUNBOOK_GENERATED = "RUNBOOK_GENERATED"

VALID_TRANSITIONS = {
    STATE_CREATED: [STATE_FIX_IDENTIFIED, STATE_CREATED],
    STATE_FIX_IDENTIFIED: [STATE_REVIEWED, STATE_FIX_IDENTIFIED],
    STATE_REVIEWED: [STATE_VERIFIED, STATE_REVIEWED],
    STATE_VERIFIED: [STATE_RUNBOOK_GENERATED, STATE_VERIFIED],
    STATE_RUNBOOK_GENERATED: [STATE_RUNBOOK_GENERATED]
}

class EventProcessor:
    """
    Event-driven processor with deduplication, idempotency, timeline ordering,
    and state machine reconciliation.
    """

    @classmethod
    def process_event(cls, db: Session, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Idempotent event processing.
        """
        event_id = event_data.get("event_id")
        event_type = event_data.get("event_type")
        source = event_data.get("source", "system")
        entity_id = event_data.get("entity_id")
        raw_timestamp = event_data.get("event_timestamp")
        payload = event_data.get("payload", {})
        version = event_data.get("version", 1)

        if isinstance(raw_timestamp, str):
            try:
                event_timestamp = datetime.datetime.fromisoformat(raw_timestamp.replace("Z", "+00:00")).replace(tzinfo=None)
            except Exception:
                event_timestamp = datetime.datetime.utcnow()
        elif isinstance(raw_timestamp, datetime.datetime):
            event_timestamp = raw_timestamp.replace(tzinfo=None) if raw_timestamp.tzinfo else raw_timestamp
        else:
            event_timestamp = datetime.datetime.utcnow()

        # 1. Deduplication / Idempotency Check (PRD §8, §18 Case 1)
        existing_event = db.query(Event).filter(Event.event_id == event_id).first()
        if existing_event:
            log = EventProcessingLog(
                event_id=event_id,
                action_taken="IGNORED_DUPLICATE",
                state_before=existing_event.status,
                state_after=existing_event.status,
                message=f"Duplicate event {event_id} detected. Skipped to prevent state corruption (Idempotency Rule 7)."
            )
            db.add(log)
            db.commit()
            return {
                "event_id": event_id,
                "action": "IGNORED_DUPLICATE",
                "message": f"Event {event_id} has already been processed. Idempotent no-op applied.",
                "entity_id": entity_id,
                "entity_type": event_type,
                "current_state": existing_event.status,
                "timestamp": datetime.datetime.utcnow()
            }

        # 2. Check for out-of-order or delayed state sequencing (PRD §9, §10)
        action_taken = "PROCESSED"
        state_before = "NONE"
        state_after = STATE_CREATED
        message = f"Event {event_id} ({event_type}) successfully processed."

        # Handle specific event types and check state machine prerequisites
        if event_type == "REVIEW_APPROVED":
            # Prerequisite: PR and fix must exist in system
            pr = db.query(PullRequest).filter(PullRequest.pr_id == entity_id).first()
            if not pr:
                # Out of order: Review arrived before PR
                action_taken = "QUEUED_OUT_OF_ORDER"
                state_before = "UNREGISTERED_PR"
                state_after = "PENDING_RECONCILIATION"
                message = f"Out-of-order event: Review {entity_id} arrived before PR was registered. Queued for reconciliation."
            else:
                state_before = STATE_FIX_IDENTIFIED
                state_after = STATE_REVIEWED
                message = f"Review approved for PR {entity_id}. Transitioned to {STATE_REVIEWED}."
                # Update PR status if merged/approved
                pr.status = "MERGED"

        elif event_type == "PR_CREATED":
            state_before = STATE_CREATED
            state_after = STATE_FIX_IDENTIFIED
            message = f"PR {entity_id} registered. Fix identified."

        elif event_type == "INCIDENT_RESOLVED":
            inc = db.query(Incident).filter(Incident.incident_id == entity_id).first()
            if inc:
                inc.resolved_at = event_timestamp
                state_before = STATE_FIX_IDENTIFIED
                state_after = STATE_REVIEWED

        elif event_type == "RUNBOOK_VERIFIED":
            state_before = STATE_REVIEWED
            state_after = STATE_VERIFIED

        # Reconstruct logical timeline: Save the event
        new_event = Event(
            event_id=event_id,
            event_type=event_type,
            source=source,
            entity_id=entity_id,
            event_timestamp=event_timestamp,
            received_at=datetime.datetime.utcnow(),
            payload=payload,
            version=version,
            status=action_taken
        )
        db.add(new_event)

        # Log action
        log = EventProcessingLog(
            event_id=event_id,
            action_taken=action_taken,
            state_before=state_before,
            state_after=state_after,
            message=message
        )
        db.add(log)
        db.commit()

        # If an out-of-order PR has just arrived, reconcile any pending reviews!
        if event_type == "PR_CREATED":
            cls.reconcile_pending_events(db, entity_id)

        return {
            "event_id": event_id,
            "action": action_taken,
            "message": message,
            "entity_id": entity_id,
            "entity_type": event_type,
            "current_state": state_after,
            "timestamp": event_timestamp
        }

    @classmethod
    def reconcile_pending_events(cls, db: Session, pr_id: str) -> None:
        """
        Reconciles any queued out-of-order review events once PR arrives.
        """
        pending_events = db.query(Event).filter(
            Event.entity_id == pr_id,
            Event.event_type == "REVIEW_APPROVED",
            Event.status == "QUEUED_OUT_OF_ORDER"
        ).order_by(Event.event_timestamp.asc()).all()

        for evt in pending_events:
            evt.status = "RECONCILED"
            log = EventProcessingLog(
                event_id=evt.event_id,
                action_taken="RECONCILED",
                state_before="PENDING_RECONCILIATION",
                state_after=STATE_REVIEWED,
                message=f"Out-of-order review event {evt.event_id} successfully reconciled with newly arrived PR {pr_id}."
            )
            db.add(log)
        db.commit()
