# Five-Minute Technical Interview Demonstration Guide

This guide provides a structured, minute-by-minute walkthrough to demonstrate TracePoint during a technical interview for an **Oracle Application Software Engineer 1** role.

---

## Overview of the 5-Minute Pitch

> *"TracePoint is an engineering intelligence and release reliability platform. Most tools treat defects as isolated tickets. TracePoint connects the entire defect lifecycle: reproducing the failure with deterministic fixtures, isolating root causes with technical evidence, validating fixes with automated regression tests, executing controlled Oracle schema migrations, and making objective release decisions based on persisted data."*

---

### Minute 1: Defect Registry & Deterministic Reproduction

- **Action**: Navigate to **Defect Registry** (`/defects`). Select **`DEF-101`** ("Scenario A: Reporting revenue query omits transaction records on midnight date boundary").
- **Walkthrough**:
  - Show the defect summary: $48,200 revenue discrepancy on monthly billing reconciliations.
  - Open the **Reproduction Details**: ordered reproduction steps, synthetic fixture reference, expected result ($75,000) vs actual result ($26,800).
  - Open **TracePoint Lab** (`/lab`), select **Scenario A**, run in **Buggy Mode**. Show how the timestamp comparison (`< 2026-09-30`) silently drops transactions occurring at `23:55:00` because the date was coerced to midnight `00:00:00`.
- **Key Technical Point**:
  > *"Instead of guessing, we reproduced the issue deterministically using synthetic boundary fixtures. The failure was isolated to an upper-bound interval omission."*

---

### Minute 2: Root-Cause Investigation Workspace

- **Action**: Navigate to **Investigation Workspace** (`/investigations`).
- **Walkthrough**:
  - Point out the 3 core conceptual layers:
    1. **Observation**: What the system actually showed ($48,200 omission).
    2. **Hypothesis**: What might explain the failure (timezone offset, date truncation, flawed BETWEEN predicate).
    3. **Confirmed Cause**: What the evidence proved (coerced midnight upper bound).
  - Inspect the **Attached Technical Evidence**: show the captured SQL query statement and execution plan.
  - Review the **Event Timeline**: immutable audit log showing when the defect was logged, reproduction attempted, hypothesis recorded, and evidence attached.
- **Key Technical Point**:
  > *"We maintain a strict separation between hypothesis and confirmed root cause. A hypothesis is never declared a root cause without supporting technical evidence."*

---

### Minute 3: Code Correction & Automated Regression Testing

- **Action**: Navigate to **TracePoint Lab** (`/lab`), switch Scenario A to **Corrected & Verified Mode**.
- **Walkthrough**:
  - Run the scenario: the corrected half-open interval `[start, end + 1 day)` captures all boundary transactions, returning the true total of $75,000.
  - Click **"Run Automated Regression Suite in Test Runner"**.
  - Show the live **Controlled Test Runner** console (`/test-runs`).
  - Demonstrate the command execution: `pytest demo_lab/tests/test_scenario_a_date_boundary.py -v`.
  - Point out that the test passed, execution duration in milliseconds, and the updated record in `TEST_RUNS`.
- **Key Technical Point**:
  > *"Every defect resolved must be accompanied by an automated regression test to permanently prevent recurrence. The test runner operates through a secure allowlist with bounded execution times."*

---

### Minute 4: Oracle Database Validation & Controlled Migrations

- **Action**: Navigate to **DB Change Validation** (`/db-changes`).
- **Walkthrough**:
  - Inspect **`001_add_performance_indexes`**:
    1. **Pre-check Query**: Asserts index `IDX_DEFECTS_COMP` does not exist in `USER_INDEXES`.
    2. **Up Migration DDL**: `CREATE INDEX idx_defects_comp ON DEFECTS (affected_component);`
    3. **Post-check Query**: Asserts index exists and status is `VALID`.
    4. **Rollback Considerations**: Explains that Oracle DDL statements issue implicit commits and cannot be rolled back with standard transaction rollback.
  - Click **"Validate & Apply Controlled Migration"**. Show the execution log confirming pre-check, execution, and post-check stages.
- **Key Technical Point**:
  > *"In Oracle, DDL operations commit implicitly. We treat schema changes as a 4-phase controlled pipeline with pre-checks, execution, post-verification queries, and documented rollback DDL."*

---

### Minute 5: Objective Release Readiness Engine

- **Action**: Navigate to **Release Readiness** (`/releases`). Select target release **`REL-2026.1.0`**.
- **Walkthrough**:
  - Show that the release status is currently **`BLOCKED`** with a readiness score of 45%.
  - Click **"Evaluate Release Readiness Engine"**.
  - Review the objective blockers identified by the gate:
    1. Failed mandatory regression test (`test_scenario_e_regression_guard`).
    2. Unresolved Critical/High defects (`DEF-101`, `DEF-102`, `DEF-104`, `DEF-105`).
    3. Pending security smoke test.
  - Explain how the engine prevents releases from being approved on human gut feeling.
- **Closing Statement**:
  > *"TracePoint proves that release readiness is an objective engineering calculation backed by persisted evidence, verified test runs, and database integrity checks."*
