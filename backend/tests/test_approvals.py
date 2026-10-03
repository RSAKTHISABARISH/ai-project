import pytest
from app.models.models import Runbook, Approval, OverrideHistory
from app.api.approvals import approve_runbook, reject_runbook, override_runbook
from app.schemas.schemas import ApprovalRequest, OverrideRequest
from fastapi import HTTPException

def test_human_approval_workflow(db_session):
    # Setup pending runbook
    rb = Runbook(
        runbook_id="RBK-TEST-APP",
        title="Test Runbook",
        issue="Issue description",
        symptoms="Symptoms",
        root_cause="Root cause",
        affected_module="Tax",
        risk_level="HIGH",
        status="PENDING_APPROVAL",
        evidence_completeness="VERIFIED"
    )
    db_session.add(rb)
    db_session.commit()

    # 1. Approve
    req = ApprovalRequest(decided_by="Lead Tax Engineer", reason="Verified math")
    approved_rb = approve_runbook("RBK-TEST-APP", req, db_session)
    assert approved_rb.status == "VERIFIED"

    approval_rec = db_session.query(Approval).filter(Approval.runbook_id == "RBK-TEST-APP").first()
    assert approval_rec is not None
    assert approval_rec.decision == "APPROVED"

def test_human_override_workflow(db_session):
    rb = Runbook(
        runbook_id="RBK-TEST-OVR",
        title="High Risk Pricing Fix",
        issue="Pricing cap exceeded",
        symptoms="Discount too high",
        root_cause="No clamp",
        affected_module="Pricing",
        risk_level="HIGH",
        status="PENDING_APPROVAL",
        evidence_completeness="VERIFIED",
        recommendations=[{"action": "Auto deploy patch"}]
    )
    db_session.add(rb)
    db_session.commit()

    # Override without reason should fail
    with pytest.raises(HTTPException):
        override_runbook("RBK-TEST-OVR", OverrideRequest(user="VP Eng", reason=""), db_session)

    # Override with mandatory reason
    ovr_req = OverrideRequest(
        user="Senior Architect Sarah",
        reason="Manual stage rollout required due to upcoming Black Friday promotion.",
        final_decision="OVERRIDDEN"
    )
    result = override_runbook("RBK-TEST-OVR", ovr_req, db_session)
    assert result.status == "OVERRIDDEN"

    # Verify audit history
    history = db_session.query(OverrideHistory).filter(OverrideHistory.runbook_id == "RBK-TEST-OVR").first()
    assert history is not None
    assert history.user == "Senior Architect Sarah"
    assert "Black Friday" in history.reason
