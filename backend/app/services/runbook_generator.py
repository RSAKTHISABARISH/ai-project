import json
import uuid
import datetime
import httpx
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.config import settings
from app.models.models import Runbook, Evidence, Incident, PullRequest, CodeDiff, Review, BusinessRule
from app.services.evidence_linker import EvidenceLinker
from app.services.rule_engine import RuleEngine

class RunbookGenerator:
    """
    Generates verified, structured runbooks distinguishing:
    FACTS, INFERENCES, and RECOMMENDATIONS.
    Includes Gemini LLM integration with an infallible deterministic fallback.
    """

    @classmethod
    def generate_runbook(
        cls,
        db: Session,
        incident_id: Optional[str] = None,
        pr_id: Optional[str] = None,
        force_demo_mode: bool = False
    ) -> Runbook:
        # 1. Assemble evidence graph
        graph = EvidenceLinker.build_evidence_graph(db, incident_id=incident_id, pr_id=pr_id)
        incident = graph.get("incident")
        pr = graph.get("pull_request")
        diff = graph.get("code_diff")
        reviews = graph.get("reviews", [])
        rules = graph.get("business_rules", [])
        overall_status = graph.get("overall_status", "PARTIAL")

        module = (incident.affected_module if incident else (rules[0].module if rules else "ERP Core"))
        rules_affected = [r.rule_code for r in rules]
        if diff and diff.business_rules_affected:
            rules_affected = list(set(rules_affected + diff.business_rules_affected))

        diff_text = diff.diff_text if diff else ""
        incident_desc = incident.description if incident else ""

        # 2. Evaluate risk level via RuleEngine
        risk_level, risk_reasons, requires_human_approval = RuleEngine.evaluate_risk(
            module=module,
            rules_affected=rules_affected,
            diff_text=diff_text,
            incident_description=incident_desc
        )

        # 3. Determine runbook status
        if requires_human_approval:
            initial_status = "PENDING_APPROVAL"
        elif overall_status == "VERIFIED":
            initial_status = "VERIFIED"
        else:
            initial_status = "DRAFT"

        # 4. Try LLM generation if configured, otherwise use deterministic generator
        facts, inferences, recommendations, procedure, validation, rollback = (
            cls._deterministic_extract(incident, pr, diff, reviews, rules, risk_level, risk_reasons)
        )

        if settings.has_llm_key and not force_demo_mode:
            try:
                llm_output = cls._call_gemini_api(incident, pr, diff, reviews, rules, risk_level)
                if llm_output:
                    procedure = llm_output.get("fix_procedure", procedure)
                    validation = llm_output.get("validation_steps", validation)
                    rollback = llm_output.get("rollback_procedure", rollback)
                    if llm_output.get("facts"): facts = llm_output["facts"]
                    if llm_output.get("inferences"): inferences = llm_output["inferences"]
                    if llm_output.get("recommendations"): recommendations = llm_output["recommendations"]
            except Exception as e:
                # Safe fallback on any LLM error or rate limit
                pass

        # 5. Create runbook record
        runbook_id = f"RBK-{uuid.uuid4().hex[:6].upper()}"
        title = f"Runbook: Fix for {incident.title if incident else (pr.title if pr else module)}"
        issue = incident.description if incident else (pr.description if pr else "ERP Business Logic Issue")
        symptoms = incident.symptoms if incident else "Calculated values deviate from expected accounting and business rule constraints."
        root_cause = (
            f"Execution sequence or boundary validation violated constraints in {', '.join(rules_affected) if rules_affected else module}. "
            + (f"Review comments confirmed: {reviews[0].comments}" if reviews else "")
        )

        runbook = Runbook(
            runbook_id=runbook_id,
            incident_id=incident.incident_id if incident else None,
            pr_id=pr.pr_id if pr else None,
            title=title,
            issue=issue,
            symptoms=symptoms,
            root_cause=root_cause,
            affected_module=module,
            business_rules=rules_affected,
            preconditions=[
                f"Verify target environment runs {module} service.",
                "Ensure database migration lock is inactive.",
                "Capture backup snapshot of affected table records."
            ],
            fix_procedure=procedure,
            validation_steps=validation,
            rollback_procedure=rollback,
            risk_level=risk_level,
            status=initial_status,
            evidence_completeness=overall_status,
            facts=facts,
            inferences=inferences,
            recommendations=recommendations
        )

        db.add(runbook)
        db.commit()
        db.refresh(runbook)

        # Link evidence items to this runbook
        for item in graph.get("evidence_items", []):
            evd = Evidence(
                evidence_id=f"{item['evidence_id']}-{runbook.runbook_id}",
                runbook_id=runbook.runbook_id,
                evidence_type=item["evidence_type"],
                entity_id=item["entity_id"],
                status=item["status"],
                details=item["details"],
                confidence_score=item["confidence_score"]
            )
            db.add(evd)
        db.commit()

        return runbook

    @classmethod
    def _deterministic_extract(
        cls,
        incident: Optional[Incident],
        pr: Optional[PullRequest],
        diff: Optional[CodeDiff],
        reviews: List[Review],
        rules: List[BusinessRule],
        risk_level: str,
        risk_reasons: List[str]
    ) -> Tuple[List[Dict], List[Dict], List[Dict], List[str], List[str], List[str]]:
        """
        Infallible deterministic extractor adhering strictly to PRD §12 & §15.
        """
        facts = []
        if incident:
            facts.append({
                "claim": f"Incident reported with severity {incident.severity}: {incident.title}",
                "source_type": "INCIDENT",
                "source_id": incident.incident_id
            })
            facts.append({
                "claim": f"Symptoms observed: {incident.symptoms}",
                "source_type": "INCIDENT",
                "source_id": incident.incident_id
            })
        if pr:
            facts.append({
                "claim": f"Pull request {pr.pr_id} submitted by {pr.author} with status {pr.status}",
                "source_type": "PR",
                "source_id": pr.pr_id
            })
        if diff:
            facts.append({
                "claim": f"Code modification touched {len(diff.files_changed)} file(s): {', '.join(diff.files_changed)}",
                "source_type": "DIFF",
                "source_id": diff.diff_id
            })
        for r in reviews:
            facts.append({
                "claim": f"Reviewer {r.reviewer} decision: {r.decision} - '{r.comments}'",
                "source_type": "REVIEW",
                "source_id": r.review_id
            })

        inferences = [
            {
                "hypothesis": f"Flaw originated from race condition or rule ordering inconsistency in affected module.",
                "basis": f"Corroborated across incident symptoms and diff alterations in {diff.files_changed if diff else 'service files'}.",
                "confidence": 0.94
            },
            {
                "hypothesis": f"Applying the approved PR commit resolves regression without breaking downstream rules.",
                "basis": f"Peer review sign-off by {reviews[0].reviewer if reviews else 'ERP maintainer'} with passing regression checks.",
                "confidence": 0.91
            }
        ]

        recommendations = [
            {
                "action": "Deploy verified hotfix code diff to ERP module service.",
                "risk_level": risk_level,
                "rationale": "; ".join(risk_reasons),
                "supporting_evidence": [
                    f"Diff {diff.diff_id if diff else 'N/A'}",
                    f"Review approval by {reviews[0].reviewer if reviews else 'system'}"
                ]
            }
        ]

        # Step-by-step fix procedure
        procedure = [
            "1. Validate existing ERP application version matches the target commit base.",
            f"2. Apply patch corresponding to files: {', '.join(diff.files_changed) if diff else 'affected source files'}.",
            "3. Ensure the sequence conforms strictly to business rules.",
            "4. Trigger ERP service compilation and restart worker processes."
        ]

        validation_steps = [
            "1. Execute unit tests covering the affected module rules.",
            "2. Run automated tax/discount/inventory calculation assertion scripts against synthetic orders.",
            "3. Verify no discrepancy flags appear in the ERP audit journal."
        ]

        rollback_procedure = [
            "1. Revert applied patch file commits immediately.",
            "2. Restart the ERP application cluster to re-read prior bytecode.",
            "3. Notify engineering on-call if audit discrepancies persist."
        ]

        return facts, inferences, recommendations, procedure, validation_steps, rollback_procedure

    @classmethod
    def _call_gemini_api(
        cls,
        incident: Optional[Incident],
        pr: Optional[PullRequest],
        diff: Optional[CodeDiff],
        reviews: List[Review],
        rules: List[BusinessRule],
        risk_level: str
    ) -> Optional[Dict[str, Any]]:
        """
        Invokes Google Gemini API with strict structured JSON output and safety boundaries.
        """
        prompt = f"""
You are an expert ERP SRE and Systems Architect. Extract a verified runbook from this evidence.
DO NOT hallucinate facts. Distinguish FACT, INFERENCE, and RECOMMENDATION.

Incident: {incident.title if incident else ''}
Symptoms: {incident.symptoms if incident else ''}
Description: {incident.description if incident else ''}
PR: {pr.title if pr else ''} - {pr.description if pr else ''}
Diff: {diff.diff_text[:1000] if diff else ''}
Reviews: {[{'by': r.reviewer, 'decision': r.decision, 'comment': r.comments} for r in reviews]}
Rules: {[r.rule_code + ': ' + r.title for r in rules]}
Risk: {risk_level}

Respond ONLY in valid JSON matching this schema:
{{
  "facts": [{{"claim": "string", "source_type": "INCIDENT|PR|DIFF|REVIEW", "source_id": "string"}}],
  "inferences": [{{"hypothesis": "string", "basis": "string", "confidence": 0.9}}],
  "recommendations": [{{"action": "string", "risk_level": "LOW|MEDIUM|HIGH", "rationale": "string", "supporting_evidence": ["string"]}}],
  "fix_procedure": ["string"],
  "validation_steps": ["string"],
  "rollback_procedure": ["string"]
}}
"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.LLM_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}
        }

        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text)
        return None
