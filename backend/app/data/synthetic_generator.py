import datetime
import uuid
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from app.models.models import (
    Incident,
    PullRequest,
    CodeDiff,
    Review,
    BusinessRule,
    Event,
    Evidence,
    Runbook,
    Approval,
    OverrideHistory,
    ExperimentResult,
    EventProcessingLog
)

MODULES = [
    "Invoice", "Tax", "Pricing", "Inventory", "Procurement",
    "Payroll", "Order Management", "Customer Management", "Payments", "Access Control"
]

RULES_DATA = [
    {
        "rule_id": "BR-001", "module": "Tax", "rule_code": "RULE-TAX-104",
        "title": "Regional discount must be applied before tax calculation",
        "description": "Any state or regional discount promo code must be subtracted from the item subtotal prior to executing the state sales tax multiplier.",
        "severity": "HIGH", "dependency_rules": ["RULE-TAX-105", "RULE-PRC-401"]
    },
    {
        "rule_id": "BR-002", "module": "Tax", "rule_code": "RULE-TAX-105",
        "title": "Cross-border VAT rate lookup must use destination country jurisdiction",
        "description": "For cross-border international sales, VAT brackets must be evaluated against the receiving destination jurisdiction instead of shipping warehouse origin.",
        "severity": "HIGH", "dependency_rules": []
    },
    {
        "rule_id": "BR-003", "module": "Inventory", "rule_code": "RULE-INV-201",
        "title": "Inventory reservation must occur before shipment confirmation",
        "description": "Physical stock count must be atomically allocated and decremented before a warehouse tracking label or shipment confirmation is generated.",
        "severity": "HIGH", "dependency_rules": ["RULE-ORD-701"]
    },
    {
        "rule_id": "BR-004", "module": "Payments", "rule_code": "RULE-PAY-301",
        "title": "Payment status must be verified before invoice closure",
        "description": "An invoice ledger record cannot transition to CLOSED or PAID status until the gateway settlement transaction ID is verified.",
        "severity": "HIGH", "dependency_rules": ["RULE-INV-201"]
    },
    {
        "rule_id": "BR-005", "module": "Pricing", "rule_code": "RULE-PRC-401",
        "title": "Customer tier volume discount cannot exceed max cap of 35%",
        "description": "Combined enterprise tiered discounts, coupon promotions, and volume rebates cannot exceed the 35% margin threshold without executive override.",
        "severity": "MEDIUM", "dependency_rules": []
    },
    {
        "rule_id": "BR-006", "module": "Procurement", "rule_code": "RULE-PRO-501",
        "title": "Procurement PO requires dual manager approval if exceeding $10,000",
        "description": "Purchase orders with lines summing over $10,000 must block vendor fulfillment until approved by both Department Lead and Finance Controller.",
        "severity": "HIGH", "dependency_rules": []
    },
    {
        "rule_id": "BR-007", "module": "Payroll", "rule_code": "RULE-PAY-601",
        "title": "Tax withholding deduction must be logged in audit ledger before payroll dispatch",
        "description": "Payroll ACH transfer batches must write dual-entry withholding debits to the federal compliance ledger before payment transmission.",
        "severity": "HIGH", "dependency_rules": ["RULE-TAX-104"]
    },
    {
        "rule_id": "BR-008", "module": "Order Management", "rule_code": "RULE-ORD-701",
        "title": "Order cancellation cannot proceed if carrier tracking number has been issued",
        "description": "Once carrier API issues an active airway bill or shipment tracking ID, order state transitions must route to RMA Return flow instead of CANCELLED.",
        "severity": "MEDIUM", "dependency_rules": ["RULE-INV-201"]
    },
    {
        "rule_id": "BR-009", "module": "Customer Management", "rule_code": "RULE-CUS-801",
        "title": "Credit limit check must validate unbilled pending invoices",
        "description": "Net-30 purchase authorization must aggregate both current open account balances and pending unbilled cart orders against credit limits.",
        "severity": "MEDIUM", "dependency_rules": ["RULE-PAY-301"]
    },
    {
        "rule_id": "BR-010", "module": "Access Control", "rule_code": "RULE-SEC-901",
        "title": "Financial transaction override requires SRE role and MFA validation",
        "description": "Manual balance adjustments or ledger rollbacks must verify SRE/Finance Admin claims with active time-based MFA session tokens.",
        "severity": "HIGH", "dependency_rules": []
    },
    {
        "rule_id": "BR-011", "module": "Invoice", "rule_code": "RULE-INV-110",
        "title": "Invoice line item tax summation must match total header rounding",
        "description": "Half-up rounding on individual line items must reconcile within 1 cent of the invoice gross header total.",
        "severity": "MEDIUM", "dependency_rules": ["RULE-TAX-104"]
    },
    {
        "rule_id": "BR-012", "module": "Inventory", "rule_code": "RULE-INV-205",
        "title": "Negative stock quantities are strictly prohibited in perpetual ledger",
        "description": "Under no concurrency condition may a warehouse bin balance drop below zero; lock escalation must throw INSUFFICIENT_STOCK exception.",
        "severity": "HIGH", "dependency_rules": ["RULE-INV-201"]
    }
]

EXPERIMENT_TASKS = [
    {
        "task_id": "EXP-001",
        "task_name": "Fix Invoice Regional Discount Tax Ordering (INC-052)",
        "module": "Tax",
        "baseline_time_mins": 42.0,
        "target_time_mins": 25.0,
        "prototype_time_mins": 18.0,
        "reduction_pct": 57.1,
        "correct_fix": True,
        "evidence_completeness": "VERIFIED",
        "failure_recovered": True,
        "error_category": None
    },
    {
        "task_id": "EXP-002",
        "task_name": "Resolve Race Condition in Inventory Reservation Lock (INC-104)",
        "module": "Inventory",
        "baseline_time_mins": 55.0,
        "target_time_mins": 30.0,
        "prototype_time_mins": 21.0,
        "reduction_pct": 61.8,
        "correct_fix": True,
        "evidence_completeness": "VERIFIED",
        "failure_recovered": True,
        "error_category": None
    },
    {
        "task_id": "EXP-003",
        "task_name": "Remediate Payment Gateway Double-Closure Bug (INC-089)",
        "module": "Payments",
        "baseline_time_mins": 48.0,
        "target_time_mins": 25.0,
        "prototype_time_mins": 19.5,
        "reduction_pct": 59.4,
        "correct_fix": True,
        "evidence_completeness": "VERIFIED",
        "failure_recovered": True,
        "error_category": None
    },
    {
        "task_id": "EXP-004",
        "task_name": "Enforce 35% Max Discount Margin Guard (INC-115)",
        "module": "Pricing",
        "baseline_time_mins": 35.0,
        "target_time_mins": 20.0,
        "prototype_time_mins": 14.0,
        "reduction_pct": 60.0,
        "correct_fix": True,
        "evidence_completeness": "VERIFIED",
        "failure_recovered": True,
        "error_category": None
    },
    {
        "task_id": "EXP-005",
        "task_name": "Correct Cross-Border VAT Jurisdiction Destination Resolution (INC-142)",
        "module": "Tax",
        "baseline_time_mins": 50.0,
        "target_time_mins": 25.0,
        "prototype_time_mins": 22.0,
        "reduction_pct": 56.0,
        "correct_fix": True,
        "evidence_completeness": "VERIFIED",
        "failure_recovered": True,
        "error_category": "Retrieval error"
    },
    {
        "task_id": "EXP-006",
        "task_name": "Fix Procurement PO Approval Escalation Routing (INC-163)",
        "module": "Procurement",
        "baseline_time_mins": 38.0,
        "target_time_mins": 20.0,
        "prototype_time_mins": 16.5,
        "reduction_pct": 56.6,
        "correct_fix": True,
        "evidence_completeness": "VERIFIED",
        "failure_recovered": True,
        "error_category": None
    },
    {
        "task_id": "EXP-007",
        "task_name": "Prevent Order Cancellation Post Carrier Tracking Assignment (INC-188)",
        "module": "Order Management",
        "baseline_time_mins": 32.0,
        "target_time_mins": 18.0,
        "prototype_time_mins": 13.0,
        "reduction_pct": 59.4,
        "correct_fix": True,
        "evidence_completeness": "VERIFIED",
        "failure_recovered": True,
        "error_category": None
    },
    {
        "task_id": "EXP-008",
        "task_name": "Reconcile Payroll Withholding Double Deduction Ledger Write (INC-204)",
        "module": "Payroll",
        "baseline_time_mins": 60.0,
        "target_time_mins": 30.0,
        "prototype_time_mins": 24.0,
        "reduction_pct": 60.0,
        "correct_fix": True,
        "evidence_completeness": "PARTIAL",
        "failure_recovered": True,
        "error_category": "Human approval error"
    },
    {
        "task_id": "EXP-009",
        "task_name": "Customer Unbilled Invoice Credit Limit Calculation Fix (INC-229)",
        "module": "Customer Management",
        "baseline_time_mins": 40.0,
        "target_time_mins": 22.0,
        "prototype_time_mins": 17.0,
        "reduction_pct": 57.5,
        "correct_fix": True,
        "evidence_completeness": "VERIFIED",
        "failure_recovered": True,
        "error_category": None
    },
    {
        "task_id": "EXP-010",
        "task_name": "Fix Session Role Validation in Financial Adjustment API (INC-251)",
        "module": "Access Control",
        "baseline_time_mins": 45.0,
        "target_time_mins": 22.0,
        "prototype_time_mins": 18.5,
        "reduction_pct": 58.9,
        "correct_fix": True,
        "evidence_completeness": "VERIFIED",
        "failure_recovered": True,
        "error_category": "LLM extraction error"
    }
]

def seed_database(db: Session, force_reset: bool = False) -> Dict[str, int]:
    """
    Seeds comprehensive synthetic ERP data: 32 Incidents, 32 PRs, 32 Diffs, 32 Reviews, 100+ Events.
    """
    if not force_reset and db.query(Incident).count() >= 30:
        return {
            "incidents": db.query(Incident).count(),
            "pull_requests": db.query(PullRequest).count(),
            "diffs": db.query(CodeDiff).count(),
            "reviews": db.query(Review).count(),
            "events": db.query(Event).count(),
            "runbooks": db.query(Runbook).count()
        }

    # Clear existing tables if reset requested
    if force_reset:
        db.query(OverrideHistory).delete()
        db.query(Approval).delete()
        db.query(Evidence).delete()
        db.query(Runbook).delete()
        db.query(EventProcessingLog).delete()
        db.query(Event).delete()
        db.query(Review).delete()
        db.query(CodeDiff).delete()
        db.query(PullRequest).delete()
        db.query(Incident).delete()
        db.query(BusinessRule).delete()
        db.query(ExperimentResult).delete()
        db.commit()

    # 1. Seed Business Rules
    for r_data in RULES_DATA:
        existing = db.query(BusinessRule).filter(BusinessRule.rule_code == r_data["rule_code"]).first()
        if not existing:
            rule = BusinessRule(**r_data)
            db.add(rule)
    db.commit()

    # 2. Seed Experiment Tasks
    for exp_data in EXPERIMENT_TASKS:
        existing = db.query(ExperimentResult).filter(ExperimentResult.task_id == exp_data["task_id"]).first()
        if not existing:
            exp = ExperimentResult(**exp_data)
            db.add(exp)
    db.commit()

    # 3. Seed Primary Showcase Scenario: INC-052 & PR-142 (PRD §27)
    now = datetime.datetime.utcnow()
    inc052_time = now - datetime.timedelta(days=2)
    
    inc052 = Incident(
        incident_id="INC-052",
        title="Incorrect invoice tax calculation due to regional discount ordering",
        description="Regional promo discounts applied post-tax calculation produced customer invoice tax overcharges in Washington and California jurisdictions violating RULE-TAX-104.",
        symptoms="Tax calculation line item in Washington jurisdiction accounts showed 9.2% rate evaluated on gross subtotal before deducting $15.00 regional coupon.",
        severity="HIGH",
        affected_module="Tax",
        discussion="Billing team noticed discrepancies during end-of-month sales tax remittance reporting. SRE traced calculation to TaxCalculationEngine.py line 84.",
        resolution="Reordered calculation sequence: DiscountCalculator.apply_regional_promo() must execute before TaxEngine.compute_sales_tax().",
        created_at=inc052_time,
        resolved_at=inc052_time + datetime.timedelta(hours=3)
    )
    db.merge(inc052)

    pr142 = PullRequest(
        pr_id="PR-142",
        incident_id="INC-052",
        title="fix(tax): Apply regional discount before sales tax calculation (RULE-TAX-104)",
        description="Resolves INC-052. Ensures regional promo codes are decremented from taxable item subtotal prior to calling state tax bracket calculation matrix.",
        author="sara.chen@enterprise-erp.io",
        status="MERGED",
        commit_id="a8f9c12b",
        reviewer_ids=["rev-marcus-99", "rev-elena-44"],
        created_at=inc052_time + datetime.timedelta(hours=1),
        merged_at=inc052_time + datetime.timedelta(hours=3)
    )
    db.merge(pr142)

    diff142 = CodeDiff(
        diff_id="DIFF-142",
        pr_id="PR-142",
        commit_id="a8f9c12b",
        files_changed=["services/tax/TaxCalculationEngine.py", "services/invoice/InvoiceSummaryBuilder.py"],
        diff_text="""--- a/services/tax/TaxCalculationEngine.py
+++ b/services/tax/TaxCalculationEngine.py
@@ -82,8 +82,9 @@ class TaxCalculationEngine:
-    tax_amount = self.calculate_state_tax(order.gross_subtotal, order.shipping_state)
-    adjusted_subtotal = self.apply_regional_discount(order.gross_subtotal, order.promo_code)
-    final_total = adjusted_subtotal + tax_amount
+    # Enforce RULE-TAX-104: Discount applied strictly prior to tax
+    taxable_subtotal = self.apply_regional_discount(order.gross_subtotal, order.promo_code)
+    tax_amount = self.calculate_state_tax(taxable_subtotal, order.shipping_state)
+    final_total = taxable_subtotal + tax_amount
     return InvoiceLine(tax_amount=tax_amount, total=final_total)""",
        business_rules_affected=["RULE-TAX-104", "RULE-TAX-105"]
    )
    db.merge(diff142)

    rev142 = Review(
        review_id="REV-142",
        pr_id="PR-142",
        reviewer="marcus.vance@enterprise-erp.io (Staff Tax Architect)",
        decision="APPROVED",
        comments="Verified calculation order adheres to RULE-TAX-104. Automated tax unit test suite passing across all 50 state matrix variations.",
        timestamp=inc052_time + datetime.timedelta(hours=2)
    )
    db.merge(rev142)

    # 4. Generate Remaining 31 Incidents, PRs, Diffs, and Reviews across the 10 ERP modules
    incident_scenarios = [
        ("INC-104", "Negative inventory balance on concurrent flash-sale checkout", "Inventory", "HIGH", "RULE-INV-201", "Inventory reservation lock was non-atomic causing race condition under high checkout concurrency."),
        ("INC-089", "Payment gateway duplicate transaction webhook closes invoice twice", "Payments", "HIGH", "RULE-PAY-301", "Webhook idempotency key was missing on retry responses causing duplicate credit ledger writes."),
        ("INC-115", "Tiered enterprise pricing exceeded 35% margin floor threshold", "Pricing", "MEDIUM", "RULE-PRC-401", "Custom coupon code stacked additively on top of wholesale volume discount without ceiling clamp."),
        ("INC-142", "Cross-border VAT rate evaluated using origin warehouse country", "Tax", "HIGH", "RULE-TAX-105", "Shipments to Germany were taxed with UK VAT rates because order header defaulted to origin warehouse jurisdiction."),
        ("INC-163", "Procurement PO exceeding $10,000 auto-dispatched without dual approval", "Procurement", "HIGH", "RULE-PRO-501", "Approval workflow branch condition checked '<=' instead of '>' for the $10,000 authorization cap."),
        ("INC-188", "Order cancellation permitted after carrier tracking label generated", "Order Management", "MEDIUM", "RULE-ORD-701", "Carrier callback status webhook lagged by 4 minutes, allowing customer self-service cancellation while parcel was on truck."),
        ("INC-204", "Payroll tax withholding deduction recorded twice in payroll run", "Payroll", "HIGH", "RULE-PAY-601", "Batch retry on network glitch re-executed withholding deduction debit lines without checking batch sequence."),
        ("INC-229", "Customer credit limit check excluded unbilled cart orders", "Customer Management", "MEDIUM", "RULE-CUS-801", "Unbilled order lines remained in temporary cache and were omitted from credit limit calculation query."),
        ("INC-251", "Unauthenticated session allowed manual ledger adjustment via internal endpoint", "Access Control", "HIGH", "RULE-SEC-901", "Internal adjustment API endpoint lacked role-based middleware check for SRE/Finance Admin authorization."),
        ("INC-262", "Invoice line item penny rounding discrepancy on multi-item split", "Invoice", "MEDIUM", "RULE-INV-110", "Half-even banker rounding differed from line-item half-up rounding resulting in 1-cent reconciliation error."),
        ("INC-275", "Sub-zero inventory quantity allowed during stock transfer", "Inventory", "HIGH", "RULE-INV-205", "Warehouse transfer API allowed source bin stock count to reach -3 units during asynchronous message consumption."),
        ("INC-288", "Customer tax exemption certificate expired but tax zeroed out", "Tax", "HIGH", "RULE-TAX-104", "Exemption certificate expiration date check was skipped when order was cloned from historical draft."),
        ("INC-301", "Payment refund triggered on chargebacked invoice without audit note", "Payments", "HIGH", "RULE-PAY-301", "Automated refund workflow processed dispute credit without writing mandatory compliance audit record."),
        ("INC-314", "Wholesale tier discount bypassed minimum order quantity requirement", "Pricing", "MEDIUM", "RULE-PRC-401", "MOQ validation check evaluated total quantity instead of per-SKU quantity requirement."),
        ("INC-328", "Procurement purchase order line currency mismatch during multi-vendor tender", "Procurement", "HIGH", "RULE-PRO-501", "Supplier quote in EUR was summed directly into USD procurement order without foreign exchange conversion."),
        ("INC-342", "Airway bill cancellation bypassed warehouse return receipt confirmation", "Order Management", "MEDIUM", "RULE-ORD-701", "Airway bill cancellation trigger did not notify warehouse staging bin to hold physical pallet."),
        ("INC-355", "Payroll salary disbursement executed without mandatory social security deduction", "Payroll", "HIGH", "RULE-PAY-601", "Contractor-to-employee conversion script omitted FICA tax flag initialization on employee profile."),
        ("INC-369", "Customer master record merged duplicate accounts with active open invoices", "Customer Management", "MEDIUM", "RULE-CUS-801", "Account deduplication script merged billing records without re-parenting pending invoice balance ledger."),
        ("INC-382", "Financial transaction approval override bypass logged empty audit trail", "Access Control", "HIGH", "RULE-SEC-901", "Audit logger failed silently on database deadlock when override approval was granted."),
        ("INC-395", "Invoice PDF export showed gross amount before line item discount", "Invoice", "MEDIUM", "RULE-INV-110", "Template engine bound to raw line price rather than discounted net price property."),
        ("INC-408", "Cross-docking inventory allocation starved backordered customer orders", "Inventory", "HIGH", "RULE-INV-201", "Inbound goods receipt allocated 100% of received stock to new orders ignoring FIFO backorder queue."),
        ("INC-421", "State sales tax rate cache expired causing fallback to 0% tax", "Tax", "HIGH", "RULE-TAX-104", "Redis cache TTL expired during high traffic and fallback handler returned zero tax rate instead of raising error."),
        ("INC-435", "Partial payment installment marked whole invoice as fully settled", "Payments", "HIGH", "RULE-PAY-301", "Settlement status update evaluated 'payment_id != null' instead of 'remaining_balance == 0'."),
        ("INC-449", "Promotional coupon code applied multiple times to recurring subscription", "Pricing", "MEDIUM", "RULE-PRC-401", "One-time promotional coupon was not marked as redeemed upon initial billing cycle completion."),
        ("INC-462", "PO requisition approval bypass for recurring monthly software vendors", "Procurement", "HIGH", "RULE-PRO-501", "Vendor master whitelist flag allowed bypass of CFO dual approval rule on contracts over $10,000."),
        ("INC-476", "Shipment routing selected decommissioned distribution center node", "Order Management", "MEDIUM", "RULE-ORD-701", "Routing engine query missed 'is_active = true' filter when querying warehouse nodes."),
        ("INC-489", "Employee overtime pay multiplier calculated against gross pay instead of base", "Payroll", "HIGH", "RULE-PAY-601", "Overtime calculation script included previous bonus payments in hourly rate denominator."),
        ("INC-502", "Credit limit authorization deadlock during bulk batch order ingestion", "Customer Management", "MEDIUM", "RULE-CUS-801", "Batch customer order importer acquired table lock on customer accounts in reverse order of transaction ID."),
        ("INC-515", "Read-only auditor role permitted executing manual payment refund API", "Access Control", "HIGH", "RULE-SEC-901", "RBAC policy router had misconfigured wildcard matching on '/api/finance/**' endpoints."),
        ("INC-528", "Invoice currency conversion rounding exceeded allowed variance threshold", "Invoice", "MEDIUM", "RULE-INV-110", "Multi-currency rounding truncated decimals instead of using half-up IEEE 754 precision standards."),
        ("INC-541", "Bin capacity constraint ignored during emergency inventory restock", "Inventory", "HIGH", "RULE-INV-205", "Warehouse restock worker process skipped maximum cubic volume verification when bin was marked hot.")
    ]

    engineers = ["elena.rostova", "marcus.vance", "liam.patel", "chloe.dupont", "amir.khan", "sarah.jenkins"]
    reviewers = ["alex.trent@enterprise-erp.io", "priya.nair@enterprise-erp.io", "hannah.schmidt@enterprise-erp.io"]

    for idx, (inc_id, inc_title, inc_mod, inc_sev, rule_code, resolution_summary) in enumerate(incident_scenarios, start=1):
        created_time = now - datetime.timedelta(days=35 - idx)
        resolved_time = created_time + datetime.timedelta(hours=4)
        pr_id = f"PR-{200 + idx}"
        diff_id = f"DIFF-{200 + idx}"
        rev_id = f"REV-{200 + idx}"
        eng = engineers[idx % len(engineers)]
        rev = reviewers[idx % len(reviewers)]

        # Incident
        inc = Incident(
            incident_id=inc_id,
            title=inc_title,
            description=f"{inc_title}. Affects {inc_mod} business workflows governed by {rule_code}.",
            symptoms=f"ERP monitoring triggered alert: inconsistencies detected in {inc_mod} service output.",
            severity=inc_sev,
            affected_module=inc_mod,
            discussion=f"Reported by ops team. Assigned to {eng} for root-cause analysis and hotfix.",
            resolution=resolution_summary,
            created_at=created_time,
            resolved_at=resolved_time
        )
        db.merge(inc)

        # Pull Request
        pr = PullRequest(
            pr_id=pr_id,
            incident_id=inc_id,
            title=f"fix({inc_mod.lower().replace(' ', '-') }): Address {inc_id} ({rule_code})",
            description=f"Fixes {inc_id}. {resolution_summary}",
            author=f"{eng}@enterprise-erp.io",
            status="MERGED",
            commit_id=f"c{uuid.uuid4().hex[:7]}",
            reviewer_ids=[rev],
            created_at=created_time + datetime.timedelta(hours=1),
            merged_at=resolved_time
        )
        db.merge(pr)

        # Code Diff
        diff = CodeDiff(
            diff_id=diff_id,
            pr_id=pr_id,
            commit_id=pr.commit_id,
            files_changed=[f"services/{inc_mod.lower().replace(' ', '_')}/core_logic.py"],
            diff_text=f"""--- a/services/{inc_mod.lower().replace(' ', '_')}/core_logic.py
+++ b/services/{inc_mod.lower().replace(' ', '_')}/core_logic.py
@@ -45,7 +45,7 @@ class ERPLogicHandler:
-    # Faulty implementation violating {rule_code}
-    result = execute_legacy_step(context)
+    # Enforced {rule_code}: {resolution_summary}
+    result = execute_validated_step(context, rule="{rule_code}")
     return result""",
            business_rules_affected=[rule_code]
        )
        db.merge(diff)

        # Review
        review = Review(
            review_id=rev_id,
            pr_id=pr_id,
            reviewer=rev,
            decision="APPROVED",
            comments=f"Verified fix for {rule_code}. Regression tests passed successfully.",
            timestamp=created_time + datetime.timedelta(hours=2)
        )
        db.merge(review)

    db.commit()

    # 5. Generate 110+ Structured Events
    event_types = ["INCIDENT_CREATED", "PR_CREATED", "REVIEW_APPROVED", "INCIDENT_RESOLVED", "RUNBOOK_VERIFIED"]
    all_prs = db.query(PullRequest).all()

    for idx, pr in enumerate(all_prs):
        # PR created event
        db.merge(Event(
            event_id=f"EVT-PR-{pr.pr_id}",
            event_type="PR_CREATED",
            source="github",
            entity_id=pr.pr_id,
            event_timestamp=pr.created_at or now,
            received_at=now,
            payload={"pr_id": pr.pr_id, "author": pr.author, "title": pr.title},
            version=1,
            status="PROCESSED"
        ))
        # Review approved event
        db.merge(Event(
            event_id=f"EVT-REV-{pr.pr_id}",
            event_type="REVIEW_APPROVED",
            source="github",
            entity_id=pr.pr_id,
            event_timestamp=(pr.created_at or now) + datetime.timedelta(hours=1),
            received_at=now,
            payload={"pr_id": pr.pr_id, "reviewer": pr.reviewer_ids[0] if pr.reviewer_ids else "architect"},
            version=1,
            status="PROCESSED"
        ))
        # Incident resolved event
        if pr.incident_id:
            db.merge(Event(
                event_id=f"EVT-INC-{pr.incident_id}",
                event_type="INCIDENT_RESOLVED",
                source="pagerduty",
                entity_id=pr.incident_id,
                event_timestamp=(pr.created_at or now) + datetime.timedelta(hours=2),
                received_at=now,
                payload={"incident_id": pr.incident_id, "status": "RESOLVED"},
                version=1,
                status="PROCESSED"
            ))

    db.commit()

    # 6. Seed Featured Verified Runbook for INC-052
    rbk052 = Runbook(
        runbook_id="RBK-TAX-052",
        incident_id="INC-052",
        pr_id="PR-142",
        title="Runbook: Fix Invoice Regional Discount Tax Ordering (RULE-TAX-104)",
        issue="Regional promo discounts applied post-tax calculation produced customer invoice tax overcharges in Washington and California jurisdictions.",
        symptoms="Sales tax amount computed on gross cart subtotal rather than discounted balance. Customers charged sales tax on promo discount amounts.",
        root_cause="TaxCalculationEngine.py evaluated calculate_state_tax before applying apply_regional_discount, in direct violation of RULE-TAX-104.",
        affected_module="Tax",
        business_rules=["RULE-TAX-104", "RULE-TAX-105"],
        preconditions=[
            "Verify ERP Tax Engine service running v4.12.0+",
            "Confirm state sales tax jurisdiction tables are synchronized.",
            "Verify transaction ledger backup has completed."
        ],
        fix_procedure=[
            "1. Inspect TaxCalculationEngine.py at lines 82-88.",
            "2. Ensure taxable_subtotal executes apply_regional_discount before calculate_state_tax.",
            "3. Update unit test assertions in test_tax_engine.py with $15 regional promo scenario.",
            "4. Deploy patch to Tax Calculation worker pods."
        ],
        validation_steps=[
            "1. Run test suite: pytest tests/test_tax_engine.py -k test_regional_discount_order.",
            "2. Generate synthetic order with Washington shipping address and $15 promo coupon.",
            "3. Assert sales tax = ($100 - $15) * 9.2% = $7.82 instead of $9.20.",
            "4. Check ERP audit journal for zero tax discrepancy flags."
        ],
        rollback_procedure=[
            "1. Revert commit a8f9c12b in TaxCalculationEngine.py.",
            "2. Re-deploy prior stable container tag to Kubernetes cluster.",
            "3. Notify on-call tax compliance specialist."
        ],
        risk_level="HIGH",
        status="VERIFIED",
        evidence_completeness="VERIFIED",
        facts=[
            {"claim": "Incident INC-052 reported tax overcharge across WA and CA jurisdictions.", "source_type": "INCIDENT", "source_id": "INC-052"},
            {"claim": "Pull Request PR-142 created by Sara Chen moved discount before tax multiplier.", "source_type": "PR", "source_id": "PR-142"},
            {"claim": "Diff DIFF-142 updated TaxCalculationEngine.py lines 82-88.", "source_type": "DIFF", "source_id": "DIFF-142"},
            {"claim": "Reviewer Marcus Vance approved PR-142 with verified state matrix tests.", "source_type": "REVIEW", "source_id": "REV-142"}
        ],
        inferences=[
            {"hypothesis": "Root cause was execution sequence inversion during legacy refactoring.", "basis": "Git blame showed commit 3 months ago re-ordered method calls.", "confidence": 0.96},
            {"hypothesis": "Fix adheres to all multi-state compliance regulations.", "basis": "Independent auditor review signed off on calculation logic.", "confidence": 0.94}
        ],
        recommendations=[
            {"action": "Deploy TaxCalculationEngine patch to production tax service.", "risk_level": "HIGH", "rationale": "Directly impacts state tax calculation and accounting ledger.", "supporting_evidence": ["DIFF-142", "REV-142", "RULE-TAX-104"]}
        ],
        created_at=now - datetime.timedelta(days=1),
        updated_at=now
    )
    db.merge(rbk052)
    db.commit()

    return {
        "incidents": db.query(Incident).count(),
        "pull_requests": db.query(PullRequest).count(),
        "diffs": db.query(CodeDiff).count(),
        "reviews": db.query(Review).count(),
        "events": db.query(Event).count(),
        "runbooks": db.query(Runbook).count()
    }
