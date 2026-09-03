# Fix2Runbook Scope Boundaries & Limitations

## 1. Scope Boundaries

Fix2Runbook is specifically designed as a **decision-support and maintenance knowledge capture assistant** for ERP enterprise engineering teams.

### Deliberate Non-Goals (What Fix2Runbook Does NOT Do)
- **Zero Autonomous Production Mutation**: Fix2Runbook does **NOT** execute shell scripts, database migrations, or hotfixes directly on production clusters without human verification.
- **No Direct Connection to Live Banking / Accounting Ledgers**: Designed to operate alongside ERP version control systems (GitHub, GitLab), incident trackers (PagerDuty, Jira), and synthetic shadow staging environments.
- **Not a Generic Chatbot**: Avoids free-form chat windows in favor of structured, evidence-grounded maintenance cards with explicit audit logging.

---

## 2. Technical Limitations

### 1. Ingestion Scope
- Currently ingests unified diff formats and git-style PR metadata. Binary blobs, proprietary ERP binary patches (e.g. SAP transports), or compiled bytecode diffs require pre-decompilation or text summarization adapters.

### 2. Multi-Repository Blast Radius
- When an ERP fix spans across 10+ microservices in distinct repositories simultaneously, evidence linking relies on common issue/incident identifiers in PR descriptions.

### 3. Local SQLite Concurrency
- Local development utilizes SQLite with WAL (Write-Ahead Logging) enabled. While suitable for prototypes and local development, high-throughput production clusters (10,000+ concurrent webhook events/sec) should transition to PostgreSQL with connection pooling.

---

## 3. Production Hardening Roadmap

1. **Enterprise SSO & OIDC Integration**: Connect human approval sign-off directly with Okta / Azure AD with hardware token MFA validation.
2. **GitOps Automated PR Creation**: Enable an approved runbook to automatically open a staging pull request via GitHub App bot credentials.
3. **Continuous Drift Detection**: Periodic background worker checking if subsequent master branch commits have invalidated previously verified runbooks.
