from app.services.rule_engine import RuleEngine

def test_financial_risk_rule():
    """
    Rule 3: Financial calculation affected -> Risk = HIGH, human approval required.
    """
    risk, reasons, human_approval = RuleEngine.evaluate_risk(
        module="Tax",
        rules_affected=["RULE-TAX-104"],
        diff_text="tax_amount = compute_tax(subtotal)"
    )
    assert risk == "HIGH"
    assert human_approval is True
    assert any("Financial or calculation logic" in r for r in reasons)

def test_data_integrity_risk_rule():
    """
    Rule 4: Database/data-integrity modification detected -> Risk = HIGH.
    """
    risk, reasons, human_approval = RuleEngine.evaluate_risk(
        module="Inventory",
        rules_affected=[],
        diff_text="execute_sql('ALTER TABLE inventory_ledger DROP COLUMN locked_stock')"
    )
    assert risk == "HIGH"
    assert human_approval is True
    assert any("Database/Data-integrity" in r for r in reasons)

def test_security_risk_rule():
    """
    Rule 5: Security/Access control changes -> Risk = HIGH.
    """
    risk, reasons, human_approval = RuleEngine.evaluate_risk(
        module="Access Control",
        rules_affected=["RULE-SEC-901"],
        diff_text="bypass_mfa_token_verification()"
    )
    assert risk == "HIGH"
    assert human_approval is True

def test_low_risk_rule():
    """
    Standard isolated non-financial change -> Risk = LOW.
    """
    risk, reasons, human_approval = RuleEngine.evaluate_risk(
        module="Customer Management",
        rules_affected=[],
        diff_text="def get_ui_theme_color(): return 'rose-gold'"
    )
    assert risk == "LOW"
    assert human_approval is False
