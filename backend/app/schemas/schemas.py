import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

# Base & Health
class HealthResponse(BaseModel):
    status: str
    version: str
    mode: str  # "AI-Assisted Mode (Gemini)" or "Deterministic / Demo Mode"
    has_llm_key: bool
    database: str
    timestamp: datetime.datetime

# Business Rule Schemas
class BusinessRuleBase(BaseModel):
    rule_id: str
    module: str
    rule_code: str
    title: str
    description: str
    severity: str = "MEDIUM"
    dependency_rules: List[str] = []

class BusinessRuleCreate(BusinessRuleBase):
    pass

class BusinessRuleOut(BusinessRuleBase):
    model_config = ConfigDict(from_attributes=True)

# Incident Schemas
class IncidentBase(BaseModel):
    incident_id: str
    title: str
    description: str
    symptoms: str
    severity: str = "MEDIUM"
    affected_module: str
    discussion: Optional[str] = None
    resolution: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    resolved_at: Optional[datetime.datetime] = None

class IncidentCreate(IncidentBase):
    pass

class IncidentOut(IncidentBase):
    model_config = ConfigDict(from_attributes=True)

# Pull Request Schemas
class PullRequestBase(BaseModel):
    pr_id: str
    incident_id: Optional[str] = None
    title: str
    description: str
    author: str
    status: str = "OPEN"
    commit_id: Optional[str] = None
    reviewer_ids: List[str] = []
    created_at: Optional[datetime.datetime] = None
    merged_at: Optional[datetime.datetime] = None

class PullRequestCreate(PullRequestBase):
    pass

class PullRequestOut(PullRequestBase):
    model_config = ConfigDict(from_attributes=True)

# Code Diff Schemas
class CodeDiffBase(BaseModel):
    diff_id: str
    pr_id: str
    commit_id: str
    files_changed: List[str] = []
    diff_text: str
    business_rules_affected: List[str] = []

class CodeDiffCreate(CodeDiffBase):
    pass

class CodeDiffOut(CodeDiffBase):
    model_config = ConfigDict(from_attributes=True)

# Review Schemas
class ReviewBase(BaseModel):
    review_id: str
    pr_id: str
    reviewer: str
    decision: str  # APPROVED, CHANGES_REQUESTED, COMMENTED
    comments: str
    timestamp: Optional[datetime.datetime] = None

class ReviewCreate(ReviewBase):
    pass

class ReviewOut(ReviewBase):
    model_config = ConfigDict(from_attributes=True)

# Event Schemas
class EventBase(BaseModel):
    event_id: str
    event_type: str
    source: str
    entity_id: str
    event_timestamp: datetime.datetime
    received_at: Optional[datetime.datetime] = None
    payload: Dict[str, Any] = {}
    version: int = 1

class EventCreate(EventBase):
    pass

class EventOut(EventBase):
    status: str
    model_config = ConfigDict(from_attributes=True)

class EventProcessResult(BaseModel):
    event_id: str
    action: str  # "PROCESSED", "IGNORED_DUPLICATE", "QUEUED_OUT_OF_ORDER", "RECONCILED"
    message: str
    entity_id: str
    entity_type: str
    current_state: str
    timestamp: datetime.datetime

# Evidence Schemas
class EvidenceItem(BaseModel):
    evidence_id: str
    evidence_type: str  # INCIDENT, PR, DIFF, REVIEW, RULE
    entity_id: str
    status: str  # VERIFIED, PARTIAL, MISSING, CONFLICTING
    details: Optional[str] = None
    confidence_score: float = 1.0

class EvidenceGraph(BaseModel):
    runbook_id: Optional[str] = None
    incident: Optional[IncidentOut] = None
    pull_request: Optional[PullRequestOut] = None
    code_diff: Optional[CodeDiffOut] = None
    reviews: List[ReviewOut] = []
    business_rules: List[BusinessRuleOut] = []
    evidence_items: List[EvidenceItem] = []
    overall_status: str  # VERIFIED, PARTIAL, MISSING, CONFLICTING
    conflict_reasons: List[str] = []

# Runbook Schemas
class RunbookFact(BaseModel):
    claim: str
    source_type: str  # INCIDENT, PR, DIFF, REVIEW
    source_id: str

class RunbookInference(BaseModel):
    hypothesis: str
    basis: str
    confidence: float

class RunbookRecommendation(BaseModel):
    action: str
    risk_level: str
    rationale: str
    supporting_evidence: List[str] = []

class RunbookGenerateRequest(BaseModel):
    incident_id: Optional[str] = None
    pr_id: Optional[str] = None
    force_demo_mode: bool = False

class RunbookOut(BaseModel):
    runbook_id: str
    incident_id: Optional[str] = None
    pr_id: Optional[str] = None
    title: str
    issue: str
    symptoms: str
    root_cause: str
    affected_module: str
    business_rules: List[str] = []
    preconditions: List[str] = []
    fix_procedure: List[str] = []
    validation_steps: List[str] = []
    rollback_procedure: List[str] = []
    risk_level: str  # LOW, MEDIUM, HIGH
    status: str  # DRAFT, PENDING_APPROVAL, APPROVED, REJECTED, OVERRIDDEN, VERIFIED
    evidence_completeness: str  # VERIFIED, PARTIAL, MISSING, CONFLICTING
    facts: List[Dict[str, Any]] = []
    inferences: List[Dict[str, Any]] = []
    recommendations: List[Dict[str, Any]] = []
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    evidence_graph: Optional[EvidenceGraph] = None
    model_config = ConfigDict(from_attributes=True)

# Human Approval Schemas
class ApprovalRequest(BaseModel):
    decided_by: str = "Lead ERP Engineer"
    reason: Optional[str] = None
    potential_impact: Optional[str] = None

class OverrideRequest(BaseModel):
    user: str = "Senior SRE Architect"
    reason: str  # Mandatory for override
    modified_procedure: Optional[List[str]] = None
    final_decision: str = "OVERRIDDEN"

class OverrideHistoryOut(BaseModel):
    id: int
    runbook_id: str
    user: str
    reason: str
    timestamp: datetime.datetime
    previous_recommendation: Optional[str] = None
    final_decision: str
    model_config = ConfigDict(from_attributes=True)

# Experiment & Metrics
class ExperimentResultOut(BaseModel):
    task_id: str
    task_name: str
    module: str
    baseline_time_mins: float
    target_time_mins: float
    prototype_time_mins: float
    reduction_pct: float
    correct_fix: bool
    evidence_completeness: str
    failure_recovered: bool
    error_category: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class MetricsSummary(BaseModel):
    total_incidents: int
    total_fixes: int
    generated_runbooks: int
    verified_runbooks: int
    pending_approvals: int
    high_risk_recommendations: int
    average_fix_time_mins: float
    baseline_fix_time_mins: float
    prototype_fix_time_mins: float
    time_reduction_percentage: float
    correct_fix_rate: float
    evidence_completeness_rate: float
    failure_recovery_rate: float
    error_taxonomy: Dict[str, int]
    tasks: List[ExperimentResultOut] = []

# Search Response
class SearchResultItem(BaseModel):
    runbook: RunbookOut
    match_score: float
    matched_by: str  # "SEMANTIC", "RULE_CODE", "KEYWORD", "INCIDENT_ID"
    evidence_status: str

class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResultItem]
