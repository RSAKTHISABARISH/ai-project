# Fix2Runbook Architecture Documentation

## 1. Executive Summary & Design Rationale

When senior ERP maintainers leave an organization, mission-critical troubleshooting knowledge is lost because historical fixes remain scattered across disparate platforms: pull requests, code diffs, reviewer approvals, and incident discussions. 

**Fix2Runbook** captures this scattered knowledge, reconciles event arrival variations, verifies supporting evidence, classifies risk, and generates production-ready, reusable runbooks for incoming engineers.

---

## 2. Technical Approach Comparison (PRD §3)

### Approach A — RAG-Centric
- **Workflow**: PRs, incidents, diffs and reviews → text embeddings → vector database → nearest-neighbor retrieval → LLM prompt → runbook output.
- **Strengths**: High flexibility with natural language queries; easy initial setup.
- **Failure Modes & Weaknesses**:
  - Unstructured ingestion cannot enforce event order or transaction consistency.
  - Zero idempotency: duplicate webhooks create duplicate vector embeddings and conflicting knowledge.
  - LLM hallucination risk: the model can fabricate preconditions or incorrect rule sequences without deterministic safety boundaries.
  - Opaque citations: difficult to guarantee that every claim is grounded in peer-reviewed diffs.

### Approach B — Event-Driven Structured System
- **Workflow**: Events → normalization → deduplication → ordering → state machine → evidence graph → rule engine → structured runbook.
- **Strengths**: Strict idempotency; out-of-order event reconciliation; deterministic safety rules; explainable evidence links.
- **Failure Modes & Weaknesses**:
  - Keyword-only searches miss natural language variations and synonyms.
  - Static templates produce rigid text lacking natural operational phrasing.

### The Selected Design: Hybrid Architecture
```
Incoming Webhook Events / PRs / Incidents
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│             Event Ingestion & Processing Layer         │
│  - Unique Event Identification                         │
│  - Idempotent Deduplication (No duplicate state)       │
│  - Logical Timeline Ordering via event_timestamp       │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│               State Machine Engine                     │
│  CREATED ──► FIX_IDENTIFIED ──► REVIEWED ──► VERIFIED   │
│  (Holds out-of-order events in reconciliation queue)   │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│           Evidence Linker & Business Rule Store        │
│  Incident ◄───► PR ◄───► Diff ◄───► Review Sign-off   │
│  Status: VERIFIED | PARTIAL | MISSING | CONFLICTING    │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│            Deterministic Rule & Risk Engine            │
│  - Rules 1 to 8 Evaluation                             │
│  - Financial / Tax / Security Risk: HIGH               │
│  - Enforces Mandatory Human-in-the-Loop Sign-off       │
└──────────────────────────┬─────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
   ┌──────────────────────┐  ┌──────────────────────┐
   │  Gemini LLM Engine   │  │ Deterministic Demo   │
   │  (When key provided) │  │ Fallback (Offline)   │
   └──────────┬───────────┘  └──────────┬───────────┘
              └────────────┬────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│             Runbook Generation & Governance            │
│  Separates: FACTS  |  INFERENCES  |  RECOMMENDATIONS   │
│  Human Approval / Override Audit History (Mandatory)   │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│         Hybrid Semantic & RAG Search Retrieval         │
│  Prioritizes: VERIFIED > PARTIAL > UNVERIFIED          │
└────────────────────────────────────────────────────────┘
```

---

## 3. Event Processing & State Machine Specifications

### Legal State Transitions
The system enforces strict directional state progression:
1. `CREATED`: Incident logged or PR initiated.
2. `FIX_IDENTIFIED`: PR and Code Diff registered.
3. `REVIEWED`: Code changes reviewed and signed off by authorized peers.
4. `VERIFIED`: Complete 4-pillar evidence alignment without rule contradictions.
5. `RUNBOOK_GENERATED`: Reusable operational runbook generated and indexed.

### Edge Case Handlers:
- **Case 1 (Duplicate Events)**: Checks incoming `event_id` against processed store. If duplicate exists, records in `EventProcessingLog`, marks as `IGNORED_DUPLICATE`, and preserves database state immutability.
- **Case 2 (Delayed Events)**: Reconstructs the logical timeline using `event_timestamp` instead of physical `received_at`.
- **Case 3 (Out-of-Order Events)**: If an approval arrives before the PR is indexed, queues event as `QUEUED_OUT_OF_ORDER`. When the PR creation event is subsequently ingested, the engine executes `reconcile_pending_events()` automatically.

---

## 4. Deterministic Rule & Risk Engine (PRD §13, §14)

- **Rule 1**: Reviewer approval existence allows verification eligibility.
- **Rule 2**: If reviewer approval is missing, status = `UNVERIFIED` / `PARTIAL`.
- **Rule 3**: Financial/tax logic modifications (e.g. Invoice, Tax, Pricing, Payroll, Payments) trigger `risk_level = HIGH` and mandate human authorization.
- **Rule 4**: Database schema / data integrity mutations (e.g., `alter table`, `drop table`, `cascade delete`) trigger `risk_level = HIGH`.
- **Rule 5**: Security, authentication, and role authorization changes trigger `risk_level = HIGH`.
- **Rule 6**: Conflicting rule definitions between incident description and code diff flag `evidence_completeness = CONFLICTING` and halt auto-approval.
- **Rule 7**: Duplicate events do not change state.
- **Rule 8**: Out-of-order events reconcile chronologically without data loss.

---

## 5. Explainable Evidence Model

Every generated runbook explicitly references its evidence lineage:
- **Incident**: ID, description, severity, symptoms.
- **Pull Request**: PR number, author, commit hash, merge status.
- **Code Diff**: Exact changed files, line additions/deletions, touched rule annotations.
- **Review**: Reviewer identity, approval status, verbatim technical commentary.
- **Business Rules**: Specific ERP rule codes (e.g. `RULE-TAX-104`, `RULE-INV-201`) and inter-rule dependencies.
