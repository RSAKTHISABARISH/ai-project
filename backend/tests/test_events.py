import datetime
from app.services.event_processor import EventProcessor
from app.models.models import Event, EventProcessingLog, PullRequest

def test_event_ingestion(db_session):
    event_data = {
        "event_id": "EVT-TEST-001",
        "event_type": "PR_CREATED",
        "source": "github",
        "entity_id": "PR-999",
        "event_timestamp": datetime.datetime.utcnow().isoformat(),
        "payload": {"title": "Test PR"},
        "version": 1
    }
    result = EventProcessor.process_event(db_session, event_data)
    assert result["action"] == "PROCESSED"
    assert result["event_id"] == "EVT-TEST-001"
    
    event_in_db = db_session.query(Event).filter(Event.event_id == "EVT-TEST-001").first()
    assert event_in_db is not None
    assert event_in_db.status == "PROCESSED"

def test_duplicate_event_idempotency(db_session):
    """
    CRITICAL PRD REQUIREMENT (§8, §18 Case 1, §26):
    Proves duplicate processing does not alter final state.
    """
    event_data = {
        "event_id": "EVT-TEST-DUP-001",
        "event_type": "PR_CREATED",
        "source": "github",
        "entity_id": "PR-999",
        "event_timestamp": datetime.datetime.utcnow().isoformat(),
        "payload": {"title": "Idempotent PR"},
        "version": 1
    }
    
    # 1. First execution
    res1 = EventProcessor.process_event(db_session, event_data)
    assert res1["action"] == "PROCESSED"
    initial_event_count = db_session.query(Event).count()
    
    # 2. Second execution with identical event_id
    res2 = EventProcessor.process_event(db_session, event_data)
    assert res2["action"] == "IGNORED_DUPLICATE"
    
    # Final state check: Event count must not increment, state must not change
    final_event_count = db_session.query(Event).count()
    assert final_event_count == initial_event_count

    # Check that audit log recorded the duplicate ignore
    log = db_session.query(EventProcessingLog).filter(
        EventProcessingLog.event_id == "EVT-TEST-DUP-001",
        EventProcessingLog.action_taken == "IGNORED_DUPLICATE"
    ).first()
    assert log is not None
    assert "Duplicate event" in log.message

def test_delayed_event_timeline(db_session):
    """
    PRD REQUIREMENT (§9, §18 Case 2):
    Late arriving events must not corrupt existing state,
    and must preserve event_timestamp as the authoritative timeline marker.
    """
    past_timestamp = datetime.datetime.utcnow() - datetime.timedelta(hours=5)
    delayed_event = {
        "event_id": "EVT-TEST-DELAYED-001",
        "event_type": "INCIDENT_RESOLVED",
        "source": "pagerduty",
        "entity_id": "INC-052",
        "event_timestamp": past_timestamp.isoformat(),
        "payload": {"resolution": "Resolved delayed"},
        "version": 2
    }
    res = EventProcessor.process_event(db_session, delayed_event)
    assert res["action"] == "PROCESSED"

    evt = db_session.query(Event).filter(Event.event_id == "EVT-TEST-DELAYED-001").first()
    assert evt is not None
    assert evt.event_timestamp.hour == past_timestamp.hour

def test_out_of_order_events_reconciliation(db_session):
    """
    CRITICAL PRD REQUIREMENT (§10, §18 Case 3, §26):
    Inject: 1. Review approval, 2. PR creation.
    Proves that out-of-order events produce the correct final state.
    """
    ooo_pr_id = "PR-OOO-TEST-99"
    now = datetime.datetime.utcnow()
    
    # 1. Inject Reviewer Approval first (Out-of-order before PR exists)
    review_event = {
        "event_id": "EVT-TEST-OOO-REV",
        "event_type": "REVIEW_APPROVED",
        "source": "github",
        "entity_id": ooo_pr_id,
        "event_timestamp": (now + datetime.timedelta(minutes=10)).isoformat(),
        "payload": {"reviewer": "architect"},
        "version": 1
    }
    res1 = EventProcessor.process_event(db_session, review_event)
    assert res1["action"] == "QUEUED_OUT_OF_ORDER"
    
    queued_event = db_session.query(Event).filter(Event.event_id == "EVT-TEST-OOO-REV").first()
    assert queued_event.status == "QUEUED_OUT_OF_ORDER"

    # 2. Register the PR entity in DB
    pr_entity = PullRequest(
        pr_id=ooo_pr_id,
        title="Out of Order PR",
        description="PR arrives late",
        author="engineer@test.io",
        status="OPEN"
    )
    db_session.add(pr_entity)
    db_session.commit()

    # 3. Inject PR Creation event
    pr_event = {
        "event_id": "EVT-TEST-OOO-PR",
        "event_type": "PR_CREATED",
        "source": "github",
        "entity_id": ooo_pr_id,
        "event_timestamp": now.isoformat(),
        "payload": {"title": "Out of Order PR"},
        "version": 1
    }
    res2 = EventProcessor.process_event(db_session, pr_event)
    assert res2["action"] == "PROCESSED"

    # Final state assertion: The out-of-order review must now be RECONCILED!
    reconciled_event = db_session.query(Event).filter(Event.event_id == "EVT-TEST-OOO-REV").first()
    assert reconciled_event.status == "RECONCILED"
