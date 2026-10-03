import datetime
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from app.database.session import Base

class Incident(Base):
    __tablename__ = "incidents"
    
    incident_id = Column(String(64), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    symptoms = Column(Text, nullable=False)
    severity = Column(String(32), default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    affected_module = Column(String(64), nullable=False, index=True)
    discussion = Column(Text, nullable=True)
    resolution = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

class PullRequest(Base):
    __tablename__ = "pull_requests"
    
    pr_id = Column(String(64), primary_key=True, index=True)
    incident_id = Column(String(64), ForeignKey("incidents.incident_id"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    author = Column(String(128), nullable=False)
    status = Column(String(32), default="OPEN")  # OPEN, MERGED, CLOSED
    commit_id = Column(String(64), nullable=True)
    reviewer_ids = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    merged_at = Column(DateTime, nullable=True)

class CodeDiff(Base):
    __tablename__ = "code_diffs"
    
    diff_id = Column(String(64), primary_key=True, index=True)
    pr_id = Column(String(64), ForeignKey("pull_requests.pr_id"), nullable=False, index=True)
    commit_id = Column(String(64), nullable=False)
    files_changed = Column(JSON, default=list)
    diff_text = Column(Text, nullable=False)
    business_rules_affected = Column(JSON, default=list)

class Review(Base):
    __tablename__ = "reviews"
    
    review_id = Column(String(64), primary_key=True, index=True)
    pr_id = Column(String(64), ForeignKey("pull_requests.pr_id"), nullable=False, index=True)
    reviewer = Column(String(128), nullable=False)
    decision = Column(String(32), nullable=False)  # APPROVED, CHANGES_REQUESTED, COMMENTED
    comments = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class BusinessRule(Base):
    __tablename__ = "business_rules"
    
    rule_id = Column(String(64), primary_key=True, index=True)
    module = Column(String(64), nullable=False, index=True)
    rule_code = Column(String(64), nullable=False, unique=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(32), default="MEDIUM")
    dependency_rules = Column(JSON, default=list)

class Event(Base):
    __tablename__ = "events"
    
    event_id = Column(String(64), primary_key=True, index=True)
    event_type = Column(String(64), nullable=False, index=True)
    source = Column(String(64), nullable=False)
    entity_id = Column(String(64), nullable=False, index=True)
    event_timestamp = Column(DateTime, nullable=False)
    received_at = Column(DateTime, default=datetime.datetime.utcnow)
    payload = Column(JSON, default=dict)
    version = Column(Integer, default=1)
    status = Column(String(32), default="PROCESSED")  # PROCESSED, DUPLICATE, OUT_OF_ORDER, RECONCILED

class Evidence(Base):
    __tablename__ = "evidence"
    
    evidence_id = Column(String(64), primary_key=True, index=True)
    runbook_id = Column(String(64), ForeignKey("runbooks.runbook_id"), nullable=True, index=True)
    evidence_type = Column(String(32), nullable=False)  # INCIDENT, PR, DIFF, REVIEW, RULE
    entity_id = Column(String(64), nullable=False)
    status = Column(String(32), default="VERIFIED")  # VERIFIED, PARTIAL, MISSING, CONFLICTING
    details = Column(Text, nullable=True)
    confidence_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Runbook(Base):
    __tablename__ = "runbooks"
    
    runbook_id = Column(String(64), primary_key=True, index=True)
    incident_id = Column(String(64), nullable=True, index=True)
    pr_id = Column(String(64), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    issue = Column(Text, nullable=False)
    symptoms = Column(Text, nullable=False)
    root_cause = Column(Text, nullable=False)
    affected_module = Column(String(64), nullable=False, index=True)
    business_rules = Column(JSON, default=list)
    preconditions = Column(JSON, default=list)
    fix_procedure = Column(JSON, default=list)
    validation_steps = Column(JSON, default=list)
    rollback_procedure = Column(JSON, default=list)
    risk_level = Column(String(32), default="MEDIUM")  # LOW, MEDIUM, HIGH
    status = Column(String(32), default="DRAFT")  # DRAFT, PENDING_APPROVAL, APPROVED, REJECTED, OVERRIDDEN, VERIFIED
    evidence_completeness = Column(String(32), default="PARTIAL")  # VERIFIED, PARTIAL, MISSING, CONFLICTING
    facts = Column(JSON, default=list)
    inferences = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Approval(Base):
    __tablename__ = "approvals"
    
    approval_id = Column(String(64), primary_key=True, index=True)
    runbook_id = Column(String(64), ForeignKey("runbooks.runbook_id"), nullable=False, index=True)
    decision = Column(String(32), nullable=False)  # APPROVED, REJECTED, OVERRIDDEN
    decided_by = Column(String(128), nullable=False)
    reason = Column(Text, nullable=True)
    potential_impact = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class OverrideHistory(Base):
    __tablename__ = "override_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    runbook_id = Column(String(64), ForeignKey("runbooks.runbook_id"), nullable=False, index=True)
    user = Column(String(128), nullable=False)
    reason = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    previous_recommendation = Column(Text, nullable=True)
    final_decision = Column(String(64), nullable=False)

class ExperimentResult(Base):
    __tablename__ = "experiment_results"
    
    task_id = Column(String(64), primary_key=True, index=True)
    task_name = Column(String(255), nullable=False)
    module = Column(String(64), nullable=False)
    baseline_time_mins = Column(Float, nullable=False)
    target_time_mins = Column(Float, nullable=False)
    prototype_time_mins = Column(Float, nullable=False)
    reduction_pct = Column(Float, nullable=False)
    correct_fix = Column(Boolean, default=True)
    evidence_completeness = Column(String(32), default="VERIFIED")
    failure_recovered = Column(Boolean, default=True)
    error_category = Column(String(64), nullable=True)

class EventProcessingLog(Base):
    __tablename__ = "event_processing_log"
    
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(64), nullable=False, index=True)
    action_taken = Column(String(64), nullable=False)  # PROCESSED, IGNORED_DUPLICATE, QUEUED_OUT_OF_ORDER, RECONCILED
    state_before = Column(String(64), nullable=True)
    state_after = Column(String(64), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    message = Column(Text, nullable=True)
