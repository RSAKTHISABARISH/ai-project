import uuid
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.models import Incident, PullRequest, CodeDiff, Review, BusinessRule, Evidence, Runbook
from app.services.rule_engine import RuleEngine

class EvidenceLinker:
    """
    Connects ERP artifacts into an Explainable Evidence Graph.
    Ensures every critical claim in a runbook maps back to verified facts.
    """

    @staticmethod
    def extract_rules_from_text(text: str) -> List[str]:
        import re
        if not text:
            return []
        matches = re.findall(r"RULE-[A-Z]+-\d+", text)
        return list(set(matches))

    @classmethod
    def build_evidence_graph(
        cls,
        db: Session,
        incident_id: Optional[str] = None,
        pr_id: Optional[str] = None
    ) -> Dict:
        """
        Traverses relationships to assemble Incident, PR, Code Diff, Reviews, and Business Rules.
        """
        incident = None
        pr = None
        diff = None
        reviews = []
        rules = []

        if incident_id:
            incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
            if not pr_id:
                # Find matching PR by incident_id or mention
                pr = db.query(PullRequest).filter(PullRequest.incident_id == incident_id).first()
                if not pr and incident:
                    # fallback match by title or description
                    pr = db.query(PullRequest).filter(PullRequest.description.contains(incident_id)).first()

        if pr_id and not pr:
            pr = db.query(PullRequest).filter(PullRequest.pr_id == pr_id).first()
            if pr and pr.incident_id and not incident:
                incident = db.query(Incident).filter(Incident.incident_id == pr.incident_id).first()

        if pr:
            diff = db.query(CodeDiff).filter(CodeDiff.pr_id == pr.pr_id).first()
            reviews = db.query(Review).filter(Review.pr_id == pr.pr_id).all()

        # Gather mentioned business rules
        extracted_rule_codes = set()
        if incident:
            extracted_rule_codes.update(cls.extract_rules_from_text(incident.description + " " + incident.title))
        if diff:
            if diff.business_rules_affected:
                extracted_rule_codes.update(diff.business_rules_affected)
            extracted_rule_codes.update(cls.extract_rules_from_text(diff.diff_text))

        if extracted_rule_codes:
            rules = db.query(BusinessRule).filter(BusinessRule.rule_code.in_(list(extracted_rule_codes))).all()

        incident_rules = cls.extract_rules_from_text((incident.description if incident else "") + " " + (incident.title if incident else ""))
        diff_rules = (diff.business_rules_affected if diff else []) or cls.extract_rules_from_text(diff.diff_text if diff else "")

        # Evaluate evidence status using RuleEngine
        overall_status, reasons = RuleEngine.evaluate_evidence_completeness(
            has_incident=incident is not None,
            has_pr=pr is not None,
            has_diff=diff is not None,
            reviews=reviews,
            incident_rules=incident_rules,
            diff_rules=diff_rules
        )

        evidence_items = []
        if incident:
            evidence_items.append({
                "evidence_id": f"EVD-INC-{incident.incident_id}",
                "evidence_type": "INCIDENT",
                "entity_id": incident.incident_id,
                "status": "VERIFIED",
                "details": f"Incident {incident.incident_id}: {incident.title} ({incident.severity})",
                "confidence_score": 1.0
            })
        if pr:
            evidence_items.append({
                "evidence_id": f"EVD-PR-{pr.pr_id}",
                "evidence_type": "PR",
                "entity_id": pr.pr_id,
                "status": "VERIFIED" if pr.status == "MERGED" else "PARTIAL",
                "details": f"PR {pr.pr_id} by {pr.author} [{pr.status}]",
                "confidence_score": 1.0 if pr.status == "MERGED" else 0.8
            })
        if diff:
            evidence_items.append({
                "evidence_id": f"EVD-DIFF-{diff.diff_id}",
                "evidence_type": "DIFF",
                "entity_id": diff.diff_id,
                "status": "VERIFIED",
                "details": f"Diff changes across {len(diff.files_changed)} file(s)",
                "confidence_score": 1.0
            })
        for r in reviews:
            evidence_items.append({
                "evidence_id": f"EVD-REV-{r.review_id}",
                "evidence_type": "REVIEW",
                "entity_id": r.review_id,
                "status": "VERIFIED" if r.decision == "APPROVED" else "PARTIAL",
                "details": f"Review by {r.reviewer}: {r.decision} - '{r.comments[:80]}...'",
                "confidence_score": 1.0 if r.decision == "APPROVED" else 0.7
            })
        for rule in rules:
            evidence_items.append({
                "evidence_id": f"EVD-RULE-{rule.rule_code}",
                "evidence_type": "RULE",
                "entity_id": rule.rule_code,
                "status": "VERIFIED",
                "details": f"{rule.rule_code}: {rule.title}",
                "confidence_score": 1.0
            })

        return {
            "incident": incident,
            "pull_request": pr,
            "code_diff": diff,
            "reviews": reviews,
            "business_rules": rules,
            "evidence_items": evidence_items,
            "overall_status": overall_status,
            "conflict_reasons": reasons
        }
