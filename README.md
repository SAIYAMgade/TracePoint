# TracePoint
### Engineering Intelligence, Root-Cause Analysis, Automated Testing & Release Reliability Platform

TracePoint is a full-stack engineering workspace built to demonstrate technical skills relevant to an **Oracle Application Software Engineer 1** role.

The distinguishing feature of TracePoint is the explicit connection between:
**Defect → Reproduction Steps → Technical Evidence → Root-Cause Analysis → Code/SQL Correction → Automated Regression Test → Release Gate Validation.**

---

## 1. Project Overview & Business Problem

In high-reliability enterprise software environments (such as financial systems, billing engines, and supply chain applications), defect management often fails because defects are treated as disconnected administrative tickets. 

When a production defect occurs:
- Symptoms are noted, but reproduction steps are missing or non-deterministic.
- Speculative hypotheses are confused with confirmed root causes.
- Fixes are deployed without automated regression tests to prevent recurrence.
- Database changes are pushed without pre-flight checks, schema validation, or rollback plans.
- Releases are declared "ready" based on subjective opinions rather than objective test evidence.

**TracePoint** solves this by unifying engineering investigation, database change validation, automated testing, and release readiness into an evidence-based system of record.

---

## 2. Technology Stack

- **Backend**: Python 3.12+ / 3.14, FastAPI, Pydantic v2, Uvicorn, Structlog.
- **Primary Relational Database**: Oracle Database Free / 19c / 21c / 23ai via `python-oracledb`.
- **Local Fallback Engine**: Embedded SQLite 3 with strict foreign key constraints (`PRAGMA foreign_keys = ON;`) and explicit dialect telemetry for zero-dependency local evaluation.
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS v4, Lucide Icons.
- **Testing & Test Runner**: Pytest, Pytest-Asyncio, Bounded Subprocess Execution, Test-suite Allowlisting.
- **CI/CD**: GitHub Actions workflow running backend tests, frontend builds, and static analysis.

---

## 3. Architecture & Data Model

### Architecture Diagram
```
┌────────────────────────────────────────────────────────┐
│             React 19 + TypeScript + Vite UI            │
│  Overview | Defects | Investigations | Tests | Release │
└──────────────────────────┬─────────────────────────────┘
                           │ HTTP / JSON with X-Correlation-ID
┌──────────────────────────▼─────────────────────────────┐
│                 FastAPI Modular Backend                │
│   Routers ──► Service Layer ──► Repositories ──► Core  │
└──────────────────────────┬─────────────────────────────┘
                           │
       ┌───────────────────┴───────────────────┐
       ▼                                       ▼
┌───────────────────────────────┐   ┌──────────────────────────┐
│   Oracle Database Free/23ai   │   │     Local SQLite Engine  │
│  Tables, Constraints, Views,  │   │   (Zero-dependency local │
│  PL/SQL Packages (PKG_DEFECT, │   │    evaluation fallback)  │
│  PKG_RELEASE_GATE)            │   │                          │
└───────────────────────────────┘   └──────────────────────────┘
```

### Relational Schema (10 Normalized Tables)
- `DEFECTS`: Core defect entity with severity, status, reproduction status, verification status, and release linkage.
- `REPRODUCTIONS`: Deterministic steps, preconditions, environment info, synthetic fixtures, and outcomes.
- `INVESTIGATIONS`: Separates **Observation**, **Hypothesis**, and **Confirmed Root Cause**.
- `INVESTIGATION_EVENTS`: Immutable timeline tracking actions from defect creation to resolution.
- `EVIDENCE`: Technical evidence repository (SQL statements, error logs, stack traces, test outputs).
- `REGRESSION_TESTS`: Automated test catalog linking tests to guarded defects.
- `TEST_RUNS`: Execution records capturing exit codes, durations, and passed/failed/skipped counts.
- `RELEASES`: Target releases, version tags, rollback plans, and objective readiness scores.
- `RELEASE_CHECKS`: Mandatory and optional checks (regression tests, blocker triage, DB migrations, smoke).
- `DATABASE_CHANGES`: Controlled 4-phase migration records (pre-check, DDL, post-check, rollback).
- `AUDIT_LOG`: Immutable, append-only transaction ledger with correlation IDs.

---

## 4. Controlled Demonstration Scenarios: TracePoint Lab

TracePoint includes an isolated demonstration service (**TracePoint Lab**) with 5 reproducible failure scenarios:

| Scenario | Component | Defect Description | Root Cause | Regression Guard |
| :--- | :--- | :--- | :--- | :--- |
| **Scenario A** | `billing-service` | Revenue query omits records on midnight date boundary (`23:59:59.000`). Discrepancy: $48,200. | End-date string comparison coerced upper bound to midnight `00:00:00`, dropping last 24 hours. | `test_scenario_a_date_boundary.py` (verifies closed/half-open boundary). |
| **Scenario B** | `order-analytics` | Order reporting query aggregates 3x-5x inflated gross totals for multi-shipment orders. | Missing subquery grouping in orders-to-shipments join caused cartesian fan-out. | `test_scenario_b_duplicate_aggregation.py` (verifies CTE aggregation). |
| **Scenario C** | `invoice-workflow` | Enterprise invoices > $50,000 transition directly from DRAFT to ISSUED. | Missing backend state machine transition validation; allowed arbitrary status update. | `test_scenario_c_invalid_transition.py` (verifies 422 validation error). |
| **Scenario D** | `settlement-processor`| Batch payment settlement commits partial rows on foreign key violation, leaving orphaned data. | Autocommit on batch runner; missing atomic transaction block with rollback on error. | `test_scenario_d_db_integrity.py` (verifies zero rows committed on failure). |
| **Scenario E** | `checkout-engine` | Speed optimization to discount calculation accidentally accepts expired coupon codes. | Expiration check nested inside fixed-dollar branch only; percentage coupons bypassed check. | `test_scenario_e_regression_guard.py` (verifies coupon rejection). |

---

## 5. Quick Start & Setup Instructions

### Prerequisites
- Python 3.12, 3.13, or 3.14.
- Node.js 20+ and npm.
- Optional: Oracle Database Free 23ai or XE/19c/21c.

### 1. Environment Configuration
Copy the configuration template:
```bash
cp .env.example .env
```
Default `.env` configuration:
```env
APP_NAME=TracePoint
APP_ENV=development
API_HOST=127.0.0.1
API_PORT=8000
DB_ENGINE=sqlite
SQLITE_DB_PATH=tracepoint.db
```

### 2. Run Automated Pytest Test Suite
Run the 28 tests across unit, API, integration, and demonstration lab suites:
```bash
python -m pytest
```
*Expected result:* 23 passed, 5 skipped (Oracle integration tests skipped when Oracle instance is not connected).

### 3. Build & Run Application
```bash
# 1. Install frontend dependencies and build production assets:
npm --prefix frontend install
npm --prefix frontend run build

# 2. Start the unified FastAPI backend & frontend server:
python scripts/start_backend.py
```
Open **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your browser to view the application.
Open **[http://127.0.0.1:8000/api/docs](http://127.0.0.1:8000/api/docs)** for interactive OpenAPI documentation.

---

## 6. Oracle Database Integration & Setup

To run against an Oracle Database Free / 23ai instance:

1. Update `.env` with your Oracle credentials:
```env
DB_ENGINE=oracle
ORACLE_USER=tracepoint_app
ORACLE_PASSWORD=your_password
ORACLE_DSN=localhost:1521/FREEPDB1
```

2. Initialize Oracle tables, views, PL/SQL packages, and seed data:
```bash
python scripts/init_oracle_db.py
```

3. Run Oracle integration tests:
```bash
python -m pytest tests/integration/test_oracle_integration.py -v
```

---

## 7. Five-Minute Technical Interview Demonstration

TracePoint is designed for a concise 5-minute technical demonstration:

- **Minute 1: Defect Registry & Reproduction**
  - Open **Defect Registry** (`/defects`), select **`DEF-101`**. Show the $48,200 revenue discrepancy.
  - Open **TracePoint Lab** (`/lab`), select **Scenario A**, run in **Buggy Mode**. Show how the date comparison drops boundary transactions.
- **Minute 2: Root-Cause Analysis**
  - Open **Investigation Workspace** (`/investigations`).
  - Demonstrate the three layers: Observation vs. Hypothesis vs. Confirmed Cause.
  - Review attached technical evidence: SQL statement and execution plan.
- **Minute 3: Automated Testing & Test Runner**
  - In TracePoint Lab, toggle to **Corrected Mode** and run.
  - Jump to **Test Runs** (`/test-runs`) and execute `pytest demo_lab/tests/test_scenario_a_date_boundary.py -v`.
  - Show the live console output, exit code, and recorded duration in ms.
- **Minute 4: Database Change Validation**
  - Open **DB Change Validation** (`/db-changes`), select `001_add_performance_indexes`.
  - Walk through pre-check, DDL, post-check, and rollback considerations.
  - Click **"Validate & Apply Controlled Migration"** and inspect execution logs.
- **Minute 5: Release Readiness Gate Engine**
  - Open **Release Readiness** (`/releases`), select `REL-2026.1.0`.
  - Show that status is **BLOCKED** (score: 45%).
  - Click **"Evaluate Release Readiness Engine"** to show objective blocking reasons (failed regression test, open critical bugs, pending smoke checks).

---

## 8. Known Limitations & Engineering Disclosures

1. **Oracle DDL Implicit Commits**: In Oracle Database, DDL operations execute implicit commits and cannot be rolled back via transactional `ROLLBACK`. Migration rollback must be executed via explicit reverse DDL scripts.
2. **Oracle Local Environment**: When a live Oracle Database instance is not reachable, the system transparently runs on SQLite with identical schema constraints, clearly labeling dialect status as `SQLite Fallback Mode`.
3. **Bounded Command Execution**: The test runner rejects non-allowlisted commands to eliminate command-injection risks.
