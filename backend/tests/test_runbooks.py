from app.services.runbook_generator import RunbookGenerator
from app.services.rag_search import RAGSearchService
from app.models.models import Runbook

def test_runbook_generation_structure(db_session):
    """
    PRD REQUIREMENT (§12, §15):
    Runbook must distinguish FACTS, INFERENCES, and RECOMMENDATIONS.
    """
    rb = RunbookGenerator.generate_runbook(db_session, incident_id="INC-052", force_demo_mode=True)
    assert rb is not None
    assert rb.runbook_id.startswith("RBK-")
    assert len(rb.facts) >= 2
    assert len(rb.inferences) >= 1
    assert len(rb.recommendations) >= 1
    assert len(rb.fix_procedure) >= 1
    assert len(rb.validation_steps) >= 1
    assert len(rb.rollback_procedure) >= 1

def test_rag_search_priority(db_session):
    """
    PRD REQUIREMENT (§17):
    Prioritize VERIFIED > PARTIAL > UNVERIFIED.
    """
    # Create unverified draft runbook with 'tax' in title
    draft_rb = Runbook(
        runbook_id="RBK-DRAFT-TAX",
        title="Draft Tax Calculation Notes",
        issue="Tax issue notes",
        symptoms="Symptoms",
        root_cause="Unknown",
        affected_module="Tax",
        risk_level="MEDIUM",
        status="DRAFT",
        evidence_completeness="MISSING"
    )
    db_session.add(draft_rb)
    db_session.commit()

    results = RAGSearchService.search(db_session, query="tax calculation")
    assert len(results) > 0
    # Top result should be the verified INC-052 runbook
    top_result = results[0]
    assert top_result["evidence_status"] == "VERIFIED"
