from app.services.evidence_linker import EvidenceLinker
from app.services.rule_engine import RuleEngine

def test_evidence_linking_inc052(db_session):
    """
    Verifies that INC-052 correctly links to PR-142, DIFF-142, and REV-142.
    """
    graph = EvidenceLinker.build_evidence_graph(db_session, incident_id="INC-052")
    assert graph["incident"] is not None
    assert graph["incident"].incident_id == "INC-052"
    assert graph["pull_request"] is not None
    assert graph["pull_request"].pr_id == "PR-142"
    assert graph["code_diff"] is not None
    assert len(graph["reviews"]) >= 1
    assert graph["overall_status"] == "VERIFIED"

def test_conflicting_evidence_detection(db_session):
    """
    PRD REQUIREMENT (§11, §18 Case 5, §26):
    Incident says one rule changed while code diff indicates another -> CONFLICTING.
    """
    status, reasons = RuleEngine.evaluate_evidence_completeness(
        has_incident=True,
        has_pr=True,
        has_diff=True,
        reviews=[],
        incident_rules=["RULE-TAX-104"],
        diff_rules=["RULE-ORD-701"]
    )
    assert status == "CONFLICTING"
    assert any("Conflict detected" in r for r in reasons)

def test_missing_evidence_detection(db_session):
    """
    PRD REQUIREMENT (§11, §18 Case 4):
    Missing diff or PR prevents VERIFIED status.
    """
    status, reasons = RuleEngine.evaluate_evidence_completeness(
        has_incident=True,
        has_pr=False,
        has_diff=False,
        reviews=[],
        incident_rules=[],
        diff_rules=[]
    )
    assert status == "MISSING"
