# TracePoint Architecture & Engineering Design

TracePoint is an engineering intelligence, root-cause investigation, automated testing, and release reliability platform designed to demonstrate technical competency relevant to an Oracle Application Software Engineer 1 role.

Unlike generic ticketing tools, TracePoint explicitly connects:
**Defect → Reproduction Steps → Technical Evidence → Investigation Hypotheses → Confirmed Root Cause → Code/SQL Correction → Automated Regression Test → Release Gate Validation.**

---

## 1. System Architecture

```mermaid
flowchart TD
    subgraph Frontend["React 19 + TypeScript + Vite UI"]
        UI_Dash["Engineering Overview Dashboard"]
        UI_Defects["Defect Registry & State Machine"]
        UI_Inv["Investigation & Evidence Workspace"]
        UI_Tests["Regression Catalog & Runner Console"]
        UI_Rel["Release Readiness Gate Matrix"]
        UI_DB["DB Change Validation Manager"]
        UI_Lab["TracePoint Lab Demo Runner"]
    end

    subgraph Backend["FastAPI Modular Backend (Python 3.14)"]
        API_Routes["REST API Layer (/api/*)"]
        Middleware["Correlation ID & Security Sanitizer"]
        
        subgraph Services["Domain Service Layer"]
            Svc_Defect["Defect Lifecycle Service (State Machine)"]
            Svc_Runner["Controlled Test Runner (Subprocess Isolation)"]
            Svc_Release["Release Gate Engine (Readiness Calculator)"]
            Svc_DB["Database Migration Validator (Pre/Up/Post)"]
        end

        subgraph Repositories["Repository / Data Access Layer"]
            Repo_Defect["DefectRepository"]
            Repo_Inv["InvestigationRepository"]
            Repo_Test["TestingRepository"]
            Repo_Rel["ReleaseRepository"]
            Repo_Audit["AuditRepository"]
        end
    end

    subgraph Storage["Relational Database Layer"]
        DB_Manager["DatabaseManager (Transparent Engine Switch)"]
        Oracle_DB[("Oracle Database Free / 23ai / 19c\n(PL/SQL Packages, Views, DDL)")]
        SQLite_DB[("SQLite 3 Engine\n(Zero-Dependency Emulation & Fallback)")]
    end

    subgraph DemoLab["TracePoint Lab Synthetic Service"]
        Scen_A["Scenario A: Date Boundary"]
        Scen_B["Scenario B: Duplicate Aggregation"]
        Scen_C["Scenario C: State Guard"]
        Scen_D["Scenario D: DB Rollback"]
        Scen_E["Scenario E: Regression Guard"]
    end

    Frontend -->|HTTP / JSON with X-Correlation-ID| API_Routes
    API_Routes --> Middleware
    Middleware --> Services
    Services --> Repositories
    Services --> Svc_Runner
    Svc_Runner -->|Bounded Execution| DemoLab
    Repositories --> DB_Manager
    DB_Manager -->|oracledb Thin/Thick Driver| Oracle_DB
    DB_Manager -->|sqlite3 Driver| SQLite_DB
```

---

## 2. Defect State Machine Architecture

Transitions between defect states are strictly validated. Critical transitions (such as moving to `VERIFIED` or `CLOSED`) reject arbitrary updates unless required technical evidence and passing regression test results exist.

```mermaid
stateDiagram-v2
    [*] --> OPEN: Log Defect
    OPEN --> REPRODUCED: Deterministic Reproduction
    OPEN --> INVESTIGATING: Direct Triage
    OPEN --> REJECTED: Invalid Issue
    OPEN --> DUPLICATE: Existing Defect
    
    REPRODUCED --> INVESTIGATING: Hypothesis Formulated
    REPRODUCED --> FIX_PROPOSED: Immediate Solution
    REPRODUCED --> INCONCLUSIVE: Intermittent / Missing Data
    
    INVESTIGATING --> FIX_PROPOSED: Root Cause Confirmed
    INVESTIGATING --> INCONCLUSIVE: Insufficient Evidence
    
    FIX_PROPOSED --> VALIDATION_REQUIRED: Code / DDL Prepared
    
    VALIDATION_REQUIRED --> VERIFIED: Regression Test Passed & Evidence Attached
    VALIDATION_REQUIRED --> FIX_PROPOSED: Test Failure / Regressed
    
    VERIFIED --> CLOSED: Release Validated
    VERIFIED --> OPEN: Reopened (Regression Detected)
    
    CLOSED --> OPEN: Reopened
    REJECTED --> OPEN: Reopened with New Info
```

---

## 3. Controlled Test Runner Architecture

TracePoint avoids unsafe arbitrary shell execution.
1. **Command Allowlist**: Only bounded, known pytest suites are executable through the runner:
   - `pytest demo_lab/tests/test_scenario_a_date_boundary.py -v`
   - `pytest demo_lab/tests/test_scenario_b_duplicate_aggregation.py -v`
   - `pytest demo_lab/tests/test_scenario_c_invalid_transition.py -v`
   - `pytest demo_lab/tests/test_scenario_d_db_integrity.py -v`
   - `pytest demo_lab/tests/test_scenario_e_regression_guard.py -v`
   - `pytest tests/unit/ -v`
   - `pytest tests/api/ -v`
   - `pytest demo_lab/tests/ -v`
2. **Execution Boundary**: Runs via `subprocess.run` with a 25-second maximum timeout.
3. **Capture & Telemetry**: Captures exact exit codes, stdout, stderr, execution duration, and extracts parsed passed/failed/skipped counts.
4. **Audit Linkage**: Automatically creates a record in `TEST_RUNS` and updates `REGRESSION_TESTS.last_outcome`.

---

## 4. Objective Release Readiness Engine

A software release cannot transition to `READY_FOR_REVIEW` or `APPROVED` merely by user preference. The Release Readiness Engine computes readiness deterministically using the following formula:

$$\text{Readiness Score} = \left( \frac{\text{Passed Checks} + \text{Waived Checks}}{\text{Total Checks}} \right) \times 100$$

A release is marked `BLOCKED` if:
1. Any mandatory release check is `FAILED` or `PENDING`.
2. Any open `CRITICAL` or `HIGH` defect linked to the release remains unresolved (`status NOT IN ('VERIFIED', 'CLOSED')`).
3. Any regression test run associated with the target release has an outcome of `FAILED`.
4. Any mandatory database migration is unapplied or failed.
