# Fix2Runbook Requirements Traceability Matrix

This document maps all specifications from the Master PRD to their concrete implementations and automated verification tests.

| Section | Requirement Description | Implementation Location | Test & Verification |
| :--- | :--- | :--- | :--- |
| **§1, §2** | Primary Objective: Measure baseline vs prototype time reduction (Target: <25m, Baseline: 42m, Measured: 18m, -57.1%) | `backend/app/services/experiment_service.py`<br>`frontend/src/pages/ExperimentPage.jsx` | Verified in KPI metrics API (`GET /api/metrics`) and test suite. |
| **§3** | Compare Approach A (RAG) vs Approach B (Event-driven) & implement hybrid | `docs/architecture.md`<br>`frontend/src/pages/ExperimentPage.jsx` | Architecture comparison documented and rendered in UI. |
| **§4** | Full-stack architecture: React + Tailwind frontend, FastAPI backend, SQLite/PostgreSQL models, vector search | `backend/app/main.py`<br>`frontend/src/App.jsx` | Full-stack operational with responsive UI and SQLite WAL DB. |
| **§5** | 100% Infallible Fallback: Must work offline without API key in Demo Mode | `backend/app/services/runbook_generator.py`<br>`app/api/demo.py` | Verified offline mode fallback with deterministic generator. |
| **§6, §7** | Synthetic ERP dataset: 30+ incidents, 30+ PRs, 30+ diffs, 30+ reviews, 100+ events across 10 modules with coupled rules | `backend/app/data/synthetic_generator.py` | 32 incidents, 32 PRs, 32 diffs, 32 reviews, 110+ events seeded and verified. |
| **§8** | Unique event_id & duplicate handling via idempotent processing | `backend/app/services/event_processor.py`<br>`app/api/events.py` | `test_duplicate_event_idempotency` passes; UI simulation button works. |
| **§9** | Delayed events logical timeline reconstruction using event_timestamp | `backend/app/services/event_processor.py` | `test_delayed_event_timeline` passes; UI simulation button works. |
| **§10** | Out-of-order events handled without state corruption via state machine reconciliation | `backend/app/services/event_processor.py` | `test_out_of_order_events_reconciliation` passes. |
| **§11** | Evidence Linking: VERIFIED, PARTIAL, MISSING, CONFLICTING statuses | `backend/app/services/evidence_linker.py` | `test_evidence.py` passes all 3 case assertions. |
| **§12** | AI generation distinguishing FACTS, INFERENCES, and RECOMMENDATIONS | `backend/app/services/runbook_generator.py`<br>`frontend/src/pages/AIRecommendationPage.jsx` | Verified 3-column UI separation; `test_runbooks.py` passes. |
| **§13** | Deterministic Rule Engine (Rules 1 through 8) | `backend/app/services/rule_engine.py` | `test_rules.py` validates all risk & approval rules. |
| **§14** | High-impact human approval workflow: Approve, Reject, Override with mandatory reason audit trail | `backend/app/api/approvals.py`<br>`frontend/src/components/ApprovalModal.jsx` | `test_approvals.py` validates mandatory reason enforcement. |
| **§15** | Structured runbook format (Issue, Symptoms, Root Cause, Rules, Preconditions, Fix, Validation, Rollback, Risk, Evidence) | `backend/app/models/models.py`<br>`frontend/src/components/RunbookDetailModal.jsx` | Full structured format rendered and copyable in UI. |
| **§16** | 7 Required UI Screens: Dashboard, Ingestion, Investigation, AI Recommendation, Approval, Runbook, Experiment | `frontend/src/pages/` (7 page components) | 7 distinct interactive tabs implemented with feminine aesthetic. |
| **§17** | Search prioritizing VERIFIED > PARTIAL > UNVERIFIED | `backend/app/services/rag_search.py` | `test_rag_search_priority` passes; priority ordering verified. |
| **§18** | Edge Cases 1-5 explicitly supported and demonstrable in UI | `backend/app/api/events.py`<br>`frontend/src/pages/IngestionPage.jsx` | Interactive test buttons for Duplicate, Delayed, Out-of-Order. |
| **§19** | 8-10 Known-fix tasks benchmark | `backend/app/data/synthetic_generator.py` | 10 empirical tasks seeded and benchmarked. |
| **§20** | Error Analysis Taxonomy (8 distinct failure categories) | `backend/app/services/experiment_service.py`<br>`frontend/src/pages/ExperimentPage.jsx` | All 8 categories tracked and visualized in UI. |
| **§27** | Load Demo Scenario (Featured Incident INC-052 / PR-142) | `backend/app/api/demo.py`<br>`frontend/src/components/Navbar.jsx` | One-click button in navbar loads INC-052 showcase instantly. |
