import re
from typing import Dict, List, Any, Tuple
from app.models.models import Incident, PullRequest, CodeDiff, Review, BusinessRule

class RuleEngine:
    """
    Deterministic Safety & Risk Rule Engine implementing PRD §13 & §14 rules.
    """

    FINANCIAL_MODULES = {"Invoice", "Tax", "Pricing", "Payroll", "Payments"}
    SECURITY_MODULES = {"Access Control", "Authentication", "Authorization", "Permissions"}
    DATA_INTEGRITY_KEYWORDS = [
        "alter table", "drop table", "truncate", "cascade delete", "migration", 
        "foreign key", "ledger", "balance", "reconciliation", "inventory reservation"
    ]

    @classmethod
    def evaluate_risk(
        cls,
        module: str,
        rules_affected: List[str],
        diff_text: str,
        incident_description: str = ""
    ) -> Tuple[str, List[str], bool]:
        """
        Evaluates risk level (LOW, MEDIUM, HIGH) and determines if human approval is mandatory.
        Returns: (risk_level, risk_reasons, human_approval_required)
        """
        reasons = []
        is_high_risk = False

        # Rule 3: Financial calculation affected
        if module in cls.FINANCIAL_MODULES or any("TAX" in r or "PAY" in r or "PRC" in r or "INV" in r for r in rules_affected):
            reasons.append(f"Financial or calculation logic in module '{module}' is directly modified.")
            is_high_risk = True

        # Rule 4: Database / Data-integrity modification detected
        diff_lower = (diff_text or "").lower()
        inc_lower = (incident_description or "").lower()
        combined_text = f"{diff_lower} {inc_lower}"
        
        found_data_risk = [kw for kw in cls.DATA_INTEGRITY_KEYWORDS if kw in combined_text]
        if found_data_risk:
            reasons.append(f"Database/Data-integrity sensitive operations identified: {', '.join(found_data_risk)}.")
            is_high_risk = True

        # Rule 5: Security / Access control logic changes
        if module in cls.SECURITY_MODULES or any("SEC" in r or "ACC" in r for r in rules_affected):
            reasons.append(f"Security or access-control authorization rules modified in module '{module}'.")
            is_high_risk = True

        if is_high_risk:
            return "HIGH", reasons, True

        # Medium risk check: Multiple business rules affected
        if len(rules_affected) > 1 or len(diff_text or "") > 600:
            reasons.append("Multi-rule impact or extensive code diff changes across ERP components.")
            return "MEDIUM", reasons, False

        reasons.append("Standard isolated bug fix with low systemic blast radius.")
        return "LOW", reasons, False

    @classmethod
    def evaluate_evidence_completeness(
        cls,
        has_incident: bool,
        has_pr: bool,
        has_diff: bool,
        reviews: List[Review],
        incident_rules: List[str],
        diff_rules: List[str]
    ) -> Tuple[str, List[str]]:
        """
        Evaluates evidence completeness (VERIFIED, PARTIAL, MISSING, CONFLICTING)
        per Rule 1, Rule 2, and Rule 6.
        """
        reasons = []

        # Check for conflicts (Rule 6)
        if incident_rules and diff_rules:
            # If rules are non-empty and have zero overlap
            overlap = set(incident_rules).intersection(set(diff_rules))
            if not overlap:
                reasons.append(f"Conflict detected: Incident references rules {incident_rules} whereas Code Diff modifies {diff_rules}.")
                return "CONFLICTING", reasons

        # Check for core artifacts (Rule 2)
        if not has_incident or not has_pr or not has_diff:
            missing_parts = []
            if not has_incident: missing_parts.append("Incident Record")
            if not has_pr: missing_parts.append("Pull Request")
            if not has_diff: missing_parts.append("Code Diff")
            reasons.append(f"Missing core evidence components: {', '.join(missing_parts)}.")
            return "MISSING", reasons

        # Check reviewer approval (Rule 1 & 2)
        approved_reviews = [r for r in reviews if r.decision == "APPROVED"]
        if not approved_reviews:
            reasons.append("Reviewer sign-off is missing or not yet approved.")
            return "PARTIAL", reasons

        reasons.append("All primary evidence pillars (Incident, PR, Diff, Review Approval) verified and rule-aligned.")
        return "VERIFIED", reasons
