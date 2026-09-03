# Fix2Runbook 🌸
### Evidence-Driven ERP Maintenance Knowledge Capture Assistant

> **Primary Objective**: Reduce the time required for a new engineer to repeat a known ERP fix.
> **Empirical Benchmark**: Baseline 42.0 min → Prototype 18.0 min (**57.1% Time Reduction**)

---

## 1. Overview & Problem Context

An ERP enterprise application contains thousands of tightly coupled business rules across modules such as **Tax, Inventory, Pricing, Payments, Procurement, Payroll, and Access Control**. 

When senior maintainers leave, their troubleshooting knowledge is lost because past fixes remain scattered across:
* **Pull requests**
* **Incident discussions**
* **Code diffs**
* **Peer reviewer commentary**
* **Signed-off resolutions**

**Fix2Runbook** captures these scattered signals, enforces event idempotency and timeline ordering, verifies evidence completeness, runs deterministic safety checks, and generates **verified, reusable runbooks** for future on-call engineers.

Designed with a neat, modern, and elegant feminine aesthetic (**Rose Quartz, Blush & Mulberry** palette with frosted glassmorphism and refined typography), this project provides a full-stack, enterprise-grade tool.

---

## 2. Key Architecture & Hybrid Design

Fix2Runbook implements a **Hybrid Architecture** combining an **Event-Driven Structured Core** with a **Deterministic Rule/Risk Engine** and **RAG/LLM Synthesis**:

```
Webhook Events / Pull Requests / Incidents
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│             Event Processing & Idempotency Layer       │
│  - Deduplication: Ignores identical events (Rule 7)    │
│  - Timeline Ordering: Uses logical event_timestamp     │
│  - State Machine: CREATED ➔ REVIEWED ➔ VERIFIED        │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│             Explainable Evidence Graph                 │
│  Links: Incident ◄──► PR ◄──► Diff ◄──► Review Sign-off│
│  Completeness: VERIFIED | PARTIAL | CONFLICTING        │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│            Deterministic Rule & Risk Engine            │
│  - Financial / Tax / Payment / Security: Risk = HIGH   │
│  - Enforces Mandatory Human Approval with Override Log │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│              AI Runbook Generation                     │
│  Strictly Separates: FACTS | INFERENCES | ACTIONS      │
│  Dual Mode: Gemini LLM Engine + Offline Fallback       │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│         RAG Semantic Search & Metrics Engine           │
│  Prioritizes: VERIFIED > PARTIAL > UNVERIFIED          │
└────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack

* **Backend**: Python 3.11+ / 3.13, FastAPI, SQLAlchemy (SQLite with WAL mode, structured for PostgreSQL), Pydantic v2, Pytest.
* **Frontend**: React 18, Tailwind CSS, Lucide Icons, Vite (Feminine Theme: Rose Gold, Blush, Mulberry, Glassmorphism).
* **AI Engine**: Google Gemini API via Generative Language API with strict 100% infallible deterministic offline fallback.
* **Containers**: Docker & Docker Compose.

---

## 4. Quickstart Guide

### Prerequisites
* Python 3.10+
* Node.js v18+ and npm

### 1. Backend Setup
```bash
cd backend
python -m pip install -r requirements.txt
cp .env.example .env
```
*(The `.env` is pre-configured with LLM and GitHub keys, with automatic fallback if credentials are absent).*

Run backend server:
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
* Backend API runs at: `http://127.0.0.1:8000`
* Interactive Swagger Docs: `http://127.0.0.1:8000/docs`

### 2. Frontend Setup
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
* Frontend Application runs at: `http://localhost:5173`

---

## 5. Automated Verification Test Suite

Run the full pytest suite:
```bash
cd backend
python -m pytest tests -v
```

### Verified Test Assertions (15/15 Passed):
* `test_duplicate_event_idempotency`: Proves identical events produce zero duplicate state alterations.
* `test_delayed_event_timeline`: Proves events arriving late are positioned accurately via `event_timestamp`.
* `test_out_of_order_events_reconciliation`: Proves out-of-order review events safely queue and reconcile upon PR arrival without state corruption.
* `test_evidence_linking_inc052`: Asserts 4-pillar linking across Incident, PR, Diff, and Review.
* `test_conflicting_evidence_detection`: Asserts rule mismatch flags `CONFLICTING` status.
* `test_financial_risk_rule`: Asserts financial/tax logic modifications trigger `HIGH` risk and mandatory approval.
* `test_human_approval_workflow`: Asserts approval state transition to `VERIFIED`.
* `test_human_override_workflow`: Asserts mandatory override reason enforcement and audit trail logging.
* `test_runbook_generation_structure`: Asserts explicit separation of FACTS, INFERENCES, and RECOMMENDATIONS.
* `test_rag_search_priority`: Asserts prioritized retrieval (`VERIFIED > PARTIAL > UNVERIFIED`).

---

## 6. Demonstration Flow (PRD §30)

1. **Open Dashboard**: View executive metrics, average fix times, and measured time reduction (-57.1%).
2. **Load Showcase Demo**: Click **"Load INC-052 Demo"** in the top navbar.
   * Incident: `INC-052` (Regional promo discounts applied post-tax calculation produced invoice overcharges).
   * Pull Request: `PR-142` (Discount moved before sales tax multiplier).
   * Rule: `RULE-TAX-104`.
   * Risk: `HIGH` (Financial/Tax calculation).
3. **Inspect Evidence Graph**: Open the **Investigation** tab to inspect the linked PR, unified code diff, reviewer comments, and coupled business rules.
4. **AI Synthesis**: View the **AI Synthesis** tab showing distinct 3-column breakdown:
   * **Grounded Facts** (with source tags: INCIDENT, PR, DIFF, REVIEW)
   * **Model Inferences** (with confidence score)
   * **Actionable Recommendations** (with supporting evidence citations)
5. **High-Impact Human Approval**:
   * Open the **Approvals** tab.
   * Click **Review, Approve or Override**.
   * Test **Reject** or **Override**: Notice mandatory reason requirement enforced.
   * Confirm **Approve**: Runbook transitions to `VERIFIED`.
6. **Simulate Event Edge Cases**: Open the **Ingestion & Events** tab:
   * Click **"Inject Duplicate Event"**: Observe idempotency filter (`IGNORED_DUPLICATE`).
   * Click **"Inject Delayed Event"**: Observe logical timeline reconstruction.
   * Click **"Inject Out-of-Order Sequence"**: Observe state machine queueing and automatic reconciliation.
7. **Semantic Search**: Open the **Runbook Base** tab:
   * Search for `"invoice tax calculation"` or `"RULE-TAX-104"`.
   * Verified runbooks appear at the top of results.
8. **Inspect Experiment Results**: Open the **Metrics & Errors** tab:
   * Review the 10 benchmark task runs.
   * Baseline: 42.0 min vs Measured: 18.0 min (**57.1% Reduction**).
   * Categorized 8-part Error Taxonomy table and recovery rates.

---

## 7. Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application & startup lifecycle
│   │   ├── config.py                # Pydantic Settings & environment
│   │   ├── api/                     # REST API routers
│   │   │   ├── events.py            # Event ingestion & edge case injection
│   │   │   ├── incidents.py         # Incident endpoints
│   │   │   ├── pull_requests.py     # PR endpoints
│   │   │   ├── diffs.py             # Code diff endpoints
│   │   │   ├── reviews.py           # Reviewer sign-off endpoints
│   │   │   ├── runbooks.py          # Runbook generation & RAG search
│   │   │   ├── approvals.py         # Human approval, rejection, and override
│   │   │   ├── metrics.py           # Experiment KPIs and business rules
│   │   │   └── demo.py              # Demo scenario loaders
│   │   ├── models/                  # SQLAlchemy ORM database models
│   │   ├── schemas/                 # Pydantic data schemas
│   │   ├── services/                # Core business engines
│   │   │   ├── event_processor.py   # State machine, idempotency & ordering
│   │   │   ├── evidence_linker.py   # 4-pillar evidence graph assembly
│   │   │   ├── rule_engine.py       # Deterministic safety & risk evaluation
│   │   │   ├── runbook_generator.py # Fact/Inference/Action runbook generator
│   │   │   ├── rag_search.py        # Priority hybrid search service
│   │   │   └── experiment_service.py# Benchmark calculations & error taxonomy
│   │   ├── data/                    # Synthetic ERP generator (32 incidents, 110+ events)
│   │   └── database/                # SQLite WAL session management
│   ├── tests/                       # 15 automated pytest assertions
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/              # Navbar, StatCard, DiffViewer, Badges, Modals
│   │   ├── pages/                   # 7 Full-featured interactive screens
│   │   ├── api/client.js            # Frontend API client
│   │   ├── App.jsx                  # Root state & modal management
│   │   ├── index.css                # Feminine glassmorphism & Tailwind styles
│   │   └── main.jsx
│   ├── tailwind.config.js           # Curated Rose Quartz / Blush / Mulberry palette
│   └── vite.config.js
├── docs/                            # In-depth architectural & benchmark documentation
│   ├── architecture.md              # Approach A vs B vs Hybrid comparison
│   ├── requirements.md              # PRD traceability matrix
│   ├── experiment.md                # 10-task benchmark methodology
│   └── limitations.md               # Scope boundaries & production roadmap
├── docker-compose.yml
└── README.md
```

---

## 8. License & Attribution

Developed as an evidence-driven maintenance knowledge capture prototype for complex enterprise ERP environments.
