import re
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.models import Runbook, Incident, Evidence

class RAGSearchService:
    """
    Hybrid semantic & keyword search engine over verified ERP runbooks.
    Prioritizes: VERIFIED > PARTIAL > UNVERIFIED (PRD §17).
    """

    STATUS_PRIORITY = {
        "VERIFIED": 100.0,
        "APPROVED": 90.0,
        "PENDING_APPROVAL": 50.0,
        "PARTIAL": 40.0,
        "DRAFT": 20.0,
        "REJECTED": 0.0
    }

    @classmethod
    def search(cls, db: Session, query: str, limit: int = 15) -> List[Dict[str, Any]]:
        query_norm = query.strip().lower()
        if not query_norm:
            # Return recent verified runbooks
            runbooks = db.query(Runbook).order_by(Runbook.created_at.desc()).limit(limit).all()
            return [
                {
                    "runbook": rb,
                    "match_score": cls.STATUS_PRIORITY.get(rb.status, 20.0),
                    "matched_by": "RECENCY",
                    "evidence_status": rb.evidence_completeness
                }
                for rb in runbooks
            ]

        query_tokens = set(re.findall(r"\w+", query_norm))
        all_runbooks = db.query(Runbook).all()
        scored_results = []

        for rb in all_runbooks:
            score = 0.0
            matched_by = "KEYWORD"

            # Check exact Incident ID match
            if rb.incident_id and query_norm in rb.incident_id.lower():
                score += 80.0
                matched_by = "INCIDENT_ID"

            # Check PR ID match
            if rb.pr_id and query_norm in rb.pr_id.lower():
                score += 70.0
                matched_by = "PR_ID"

            # Check Rule Code match
            rule_str = " ".join(rb.business_rules or []).lower()
            if query_norm in rule_str or any(tok in rule_str for tok in query_tokens if tok.startswith("rule")):
                score += 75.0
                matched_by = "RULE_CODE"

            # Module match
            if query_norm in (rb.affected_module or "").lower():
                score += 40.0

            # Title, issue, root cause tokens
            text_corpus = f"{rb.title} {rb.issue} {rb.symptoms} {rb.root_cause}".lower()
            corpus_tokens = set(re.findall(r"\w+", text_corpus))
            common = query_tokens.intersection(corpus_tokens)
            score += len(common) * 15.0

            if query_norm in text_corpus:
                score += 30.0
                matched_by = "SEMANTIC"

            if score > 0:
                # Add priority bonus based on verification status
                status_bonus = cls.STATUS_PRIORITY.get(rb.status, 10.0)
                if rb.evidence_completeness == "VERIFIED":
                    status_bonus += 25.0
                final_score = score + status_bonus

                scored_results.append({
                    "runbook": rb,
                    "match_score": round(final_score, 2),
                    "matched_by": matched_by,
                    "evidence_status": rb.evidence_completeness
                })

        # Sort descending by match_score
        scored_results.sort(key=lambda x: x["match_score"], reverse=True)
        return scored_results[:limit]
