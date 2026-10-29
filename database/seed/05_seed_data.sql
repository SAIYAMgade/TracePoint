-- ============================================================================
-- TRACEPOINT SEED DATA
-- Realistic Engineering Scenarios for Oracle ASE-1 Demonstration
-- ============================================================================

-- RELEASES
INSERT INTO RELEASES (release_id, version_tag, summary, status, rollback_plan, is_ready, readiness_score, created_at, updated_at, released_at)
VALUES (
    'REL-2026.0.9',
    'v2026.0.9',
    'Q3 Maintenance release: patch for memory leak in event consumer and logging optimizations.',
    'RELEASED',
    'Revert container image to sha256:8f4c2e1, execute rollback script DDL-202609-REV.',
    1,
    100,
    TIMESTAMP '2026-09-15 08:00:00',
    TIMESTAMP '2026-09-20 18:00:00',
    TIMESTAMP '2026-09-20 18:30:00'
);

INSERT INTO RELEASES (release_id, version_tag, summary, status, rollback_plan, is_ready, readiness_score, created_at, updated_at)
VALUES (
    'REL-2026.1.0',
    'v2026.1.0-RC1',
    'Core business release: billing date-boundary fix, aggregate query optimization, and constraint enforcement.',
    'BLOCKED',
    'Roll back to tag v2026.0.9. Drop patch tables via migration rollback 002. Re-route gateway traffic to pool A.',
    0,
    45,
    TIMESTAMP '2026-10-10 09:00:00',
    CURRENT_TIMESTAMP
);

-- DEFECTS
INSERT INTO DEFECTS (defect_id, title, description, severity, priority, affected_component, environment, status, reproduction_status, expected_behavior, actual_behavior, root_cause_explanation, proposed_correction, verification_status, assigned_owner, associated_regression_test_id, associated_release_id, created_at, updated_at)
VALUES (
    'DEF-101',
    'Scenario A: Reporting revenue query omits transaction records on midnight date boundary',
    'Monthly revenue reconciliations showed a $48,200 discrepancy compared to ledger totals. All missing transactions had timestamps between 23:59:59.000 and 00:00:00.000.',
    'HIGH',
    'P1',
    'billing-service',
    'STAGING',
    'INVESTIGATING',
    'REPRODUCED',
    'All transactions strictly within the closed interval [start_date, end_date 23:59:59.999] should be included.',
    'Query used "transaction_time < end_date" where end_date was coerced to midnight 00:00:00 of the final day, discarding the entire final 24 hours of sales.',
    'Date boundary truncation coerced end_date without adding time component or using exclusive half-open interval.',
    'Refactor filter to half-open interval [start_date, end_date + 1 day) or TRUNC comparison in Oracle SQL.',
    'IN_PROGRESS',
    'alex.chen',
    'TEST-SCENARIO-A',
    'REL-2026.1.0',
    TIMESTAMP '2026-10-12 10:15:00',
    CURRENT_TIMESTAMP
);

INSERT INTO DEFECTS (defect_id, title, description, severity, priority, affected_component, environment, status, reproduction_status, expected_behavior, actual_behavior, root_cause_explanation, proposed_correction, verification_status, assigned_owner, associated_regression_test_id, associated_release_id, created_at, updated_at)
VALUES (
    'DEF-102',
    'Scenario B: Order item report aggregates duplicate row sums from missing join predicate',
    'Daily order summary report showed gross sales at 3x to 5x actual invoiced amounts for multi-shipment orders.',
    'CRITICAL',
    'P1',
    'order-analytics',
    'STAGING',
    'FIX_PROPOSED',
    'REPRODUCED',
    'Gross sales should equal the sum of distinct order item totals.',
    'Joining ORDERS -> ORDER_ITEMS -> SHIPMENTS without aggregating at line-item level created a cartesian fan-out on orders with multiple shipments.',
    'Cartesian fan-out caused by missing subquery aggregation or missing join predicate on shipment fulfillment records.',
    'Rewrite report query with CTE aggregating shipments prior to joining with order items.',
    'UNVERIFIED',
    'sarah.jenkins',
    'TEST-SCENARIO-B',
    'REL-2026.1.0',
    TIMESTAMP '2026-10-14 14:20:00',
    CURRENT_TIMESTAMP
);

INSERT INTO DEFECTS (defect_id, title, description, severity, priority, affected_component, environment, status, reproduction_status, expected_behavior, actual_behavior, root_cause_explanation, proposed_correction, verification_status, assigned_owner, associated_regression_test_id, associated_release_id, created_at, updated_at)
VALUES (
    'DEF-103',
    'Scenario C: Invoice status bypasses credit approval state transition directly to issued',
    'High-value enterprise invoices over $50k transitioned from DRAFT directly to ISSUED without passing mandatory CREDIT_APPROVED state.',
    'MEDIUM',
    'P2',
    'invoice-workflow',
    'STAGING',
    'VALIDATION_REQUIRED',
    'REPRODUCED',
    'Invoice transition from DRAFT to ISSUED must fail with HTTP 422 if invoice total > $50,000 and credit check is missing.',
    'Frontend triggered direct issue endpoint which lacked backend state machine transition validation.',
    'Direct status setter allowed arbitrary state assignment instead of executing state machine transition guard.',
    'Implement state machine validation in backend service and enforce through database trigger/package.',
    'IN_PROGRESS',
    'marcus.vance',
    'TEST-SCENARIO-C',
    'REL-2026.1.0',
    TIMESTAMP '2026-10-16 11:30:00',
    CURRENT_TIMESTAMP
);

INSERT INTO DEFECTS (defect_id, title, description, severity, priority, affected_component, environment, status, reproduction_status, expected_behavior, actual_behavior, root_cause_explanation, proposed_correction, verification_status, assigned_owner, associated_regression_test_id, associated_release_id, created_at, updated_at)
VALUES (
    'DEF-104',
    'Scenario D: Batch settlement leaves orphaned records on foreign key constraint violation',
    'When a batch payment settlement encountered an invalid merchant ID, partial transaction rows were committed, causing orphaned settlement lines.',
    'HIGH',
    'P1',
    'settlement-processor',
    'STAGING',
    'REPRODUCED',
    'Database foreign key constraint must be enforced; if any line fails, the entire batch transaction must ROLLBACK.',
    'Process committed batches in chunks without atomic transaction boundary, swallowing ORA-02291 integrity violation.',
    'Autocommit mode enabled on batch runner; missing explicit transaction context and exception handler rollback.',
    'Wrap batch execution in explicit database transaction with ROLLBACK in OTHERS exception handler.',
    'UNVERIFIED',
    'priya.nair',
    'TEST-SCENARIO-D',
    'REL-2026.1.0',
    TIMESTAMP '2026-10-18 16:45:00',
    CURRENT_TIMESTAMP
);

INSERT INTO DEFECTS (defect_id, title, description, severity, priority, affected_component, environment, status, reproduction_status, expected_behavior, actual_behavior, root_cause_explanation, proposed_correction, verification_status, assigned_owner, associated_regression_test_id, associated_release_id, created_at, updated_at)
VALUES (
    'DEF-105',
    'Scenario E: Discount calculation optimization causes regression in coupon validity check',
    'Refactoring discount logic for speed accidentally bypassed the expiration date check for percentage-off coupons.',
    'HIGH',
    'P2',
    'checkout-engine',
    'DEVELOPMENT',
    'OPEN',
    'REPRODUCED',
    'Expired coupons should be rejected even with the new cached discount pricing rule.',
    'Expired coupons are accepted because date check was moved inside a branch that does not execute for percentage coupons.',
    'Logic flaw in refactored calculation condition; missing regression test before merge.',
    'Restore expiration check to base validation path and add automated regression test.',
    'UNVERIFIED',
    'elena.rostova',
    'TEST-SCENARIO-E',
    'REL-2026.1.0',
    TIMESTAMP '2026-10-20 09:10:00',
    CURRENT_TIMESTAMP
);

-- REPRODUCTIONS
INSERT INTO REPRODUCTIONS (reproduction_id, defect_id, preconditions, environment_info, app_version, steps_json, synthetic_fixture_ref, expected_result, actual_result, error_message, frequency, outcome, notes, executed_by, created_at)
VALUES (
    'REP-101',
    'DEF-101',
    'Seeded transactions with timestamps 2026-09-30 14:00:00 and 2026-09-30 23:55:00.',
    'Staging Oracle DB 23ai, Python FastAPI billing-service',
    'v2026.1.0-RC1',
    '["1. Send GET /api/lab/scenarios/date-boundary?start=2026-09-01&end=2026-09-30", "2. Inspect returned transaction list and total sum", "3. Check if transaction TXN-EOM-999 is present"]',
    'fixtures/date_boundary_transactions.json',
    'Report should return 3 transactions totaling $75,000.',
    'Report returned 2 transactions totaling $26,800. TXN-EOM-999 ($48,200) was excluded.',
    'No exception thrown. Silent data omission due to SQL boundary condition.',
    'ALWAYS',
    'REPRODUCED',
    'Root cause confirmed via query execution plan inspection.',
    'alex.chen',
    TIMESTAMP '2026-10-12 11:30:00'
);

-- INVESTIGATIONS
INSERT INTO INVESTIGATIONS (investigation_id, defect_id, problem_statement, observed_symptoms, initial_hypothesis, candidate_causes, confirmed_root_cause, proposed_correction, regression_risk, verification_plan, final_conclusion, status, lead_investigator, created_at, updated_at)
VALUES (
    'INV-101',
    'DEF-101',
    'Transactions occurring on the last day of a billing cycle are silently dropped from periodic revenue queries.',
    'Discrepancy of $48,200 on 2026-09-30. Query returned fewer rows than physical table scan with equal dates.',
    'Query is using < end_date instead of <= or half-open [start, end + 1 day).',
    '1. Timezone offset between app server (UTC) and DB (EST).\n2. Date truncation stripping 23:59:59 time component.\n3. Flawed BETWEEN predicate behavior with Oracle TIMESTAMP.',
    'Application parses end_date as YYYY-MM-DD 00:00:00.000. Using < operator excluded all transactions from 00:00:01 through 23:59:59 on the final day.',
    'Adopt standard half-open interval: created_at >= :start_date AND created_at < :end_date + INTERVAL ''1'' DAY.',
    'Low risk to existing queries; potential impact on reports relying on legacy truncated totals.',
    'Run automated regression suite test_scenario_a_date_boundary with synthetic end-of-day fixtures.',
    'Defect verified and isolated to interval comparison logic. Fixed and ready for regression suite execution.',
    'ROOT_CAUSE_IDENTIFIED',
    'alex.chen',
    TIMESTAMP '2026-10-12 11:45:00',
    CURRENT_TIMESTAMP
);

INSERT INTO INVESTIGATIONS (investigation_id, defect_id, problem_statement, observed_symptoms, initial_hypothesis, candidate_causes, confirmed_root_cause, proposed_correction, regression_risk, verification_plan, final_conclusion, status, lead_investigator, created_at, updated_at)
VALUES (
    'INV-102',
    'DEF-102',
    'Multi-shipment order totals are multiplied by the count of shipments in the analytic reporting view.',
    'Orders with 3 shipments show item amounts summed 3 times in aggregate report.',
    'JOIN between ORDER_ITEMS and SHIPMENT_ITEMS missing composite key on line_number.',
    '1. Cross join due to missing WHERE clause.\n2. 1-to-many join fan-out without grouping.\n3. Accidental duplicate rows in base ORDERS table.',
    'Analytic query joins ORDERS to SHIPMENTS on order_id. Because multiple shipments exist per order, each order line was duplicated for every shipment record prior to SUM(amount).',
    'Aggregate shipment metrics in an inline view or CTE before joining with order lines, or sum distinct line item IDs.',
    'Moderate. Reporting queries across all operational dashboards should be reviewed for similar joins.',
    'Run automated regression suite test_scenario_b_duplicate_aggregation with multi-shipment fixtures.',
    'Fix proposed with CTE aggregation. Regression test written.',
    'IN_PROGRESS',
    'sarah.jenkins',
    TIMESTAMP '2026-10-14 15:00:00',
    CURRENT_TIMESTAMP
);

-- INVESTIGATION EVENTS (Timeline)
INSERT INTO INVESTIGATION_EVENTS (event_id, investigation_id, event_type, title, details, actor, created_at)
VALUES (
    'EVT-101',
    'INV-101',
    'DEFECT_CREATED',
    'Defect logged by reconciliation auditor',
    'End of month revenue discrepancy reported from financial audit team.',
    'reconciler.bot',
    TIMESTAMP '2026-10-12 10:15:00'
);

INSERT INTO INVESTIGATION_EVENTS (event_id, investigation_id, event_type, title, details, actor, created_at)
VALUES (
    'EVT-102',
    'INV-101',
    'REPRODUCTION_ATTEMPTED',
    'Deterministic reproduction executed with synthetic fixture',
    'Reproduction REP-101 executed against staging database. Discrepancy confirmed 100%.',
    'alex.chen',
    TIMESTAMP '2026-10-12 11:30:00'
);

INSERT INTO INVESTIGATION_EVENTS (event_id, investigation_id, event_type, title, details, actor, created_at)
VALUES (
    'EVT-103',
    'INV-101',
    'HYPOTHESIS_RECORDED',
    'Hypothesis formulated: Date boundary truncation',
    'Suspect query uses YYYY-MM-DD 00:00:00 as upper bound, omitting last 24 hours.',
    'alex.chen',
    TIMESTAMP '2026-10-12 11:50:00'
);

INSERT INTO INVESTIGATION_EVENTS (event_id, investigation_id, event_type, title, details, actor, created_at)
VALUES (
    'EVT-104',
    'INV-101',
    'EVIDENCE_ATTACHED',
    'SQL statement and query execution plan attached',
    'Captured SQL query showing WHERE created_at < TO_DATE(:p_end_date, ''YYYY-MM-DD'').',
    'alex.chen',
    TIMESTAMP '2026-10-12 12:15:00'
);

-- EVIDENCE
INSERT INTO EVIDENCE (evidence_id, defect_id, investigation_id, evidence_type, title, error_code, sanitized_payload, component, environment, correlation_id, collected_by, created_at)
VALUES (
    'EVI-101',
    'DEF-101',
    'INV-101',
    'SQL_STATEMENT',
    'Flawed date query statement from repository',
    'SQL-DATE-FLAW',
    'SELECT SUM(amount) FROM billing_transactions WHERE txn_date >= :p_start AND txn_date < :p_end; -- :p_end is parsed as 2026-09-30 00:00:00',
    'billing-service',
    'STAGING',
    'CORR-BILL-1001',
    'alex.chen',
    TIMESTAMP '2026-10-12 12:15:00'
);

INSERT INTO EVIDENCE (evidence_id, defect_id, investigation_id, evidence_type, title, error_code, sanitized_payload, component, environment, correlation_id, collected_by, created_at)
VALUES (
    'EVI-102',
    'DEF-104',
    NULL,
    'ERROR_LOG',
    'Oracle ORA-02291 Integrity Constraint Violation Log',
    'ORA-02291',
    'ORA-02291: integrity constraint (TRACEPOINT.FK_SETTLE_MERCHANT) violated - parent key not found. Query: INSERT INTO SETTLEMENT_LINES VALUES (...) failed for merchant_id: M-UNKNOWN.',
    'settlement-processor',
    'STAGING',
    'CORR-SETTLE-409',
    'priya.nair',
    TIMESTAMP '2026-10-18 16:50:00'
);

-- REGRESSION TESTS
INSERT INTO REGRESSION_TESTS (test_id, title, description, test_category, related_defect_id, preconditions, expected_behavior, execution_command, last_outcome, last_run_at, created_at)
VALUES (
    'TEST-SCENARIO-A',
    'Verify midnight date boundary includes all final-day transactions',
    'Tests billing aggregation for transactions occurring between 00:00:00 and 23:59:59 on the boundary date.',
    'REGRESSION',
    'DEF-101',
    'Synthetic transactions seeded at 2026-09-30 23:59:59.000',
    'Sum must include boundary transactions without omission.',
    'pytest demo_lab/tests/test_scenario_a_date_boundary.py -v',
    'PASSED',
    CURRENT_TIMESTAMP,
    TIMESTAMP '2026-10-13 09:00:00'
);

INSERT INTO REGRESSION_TESTS (test_id, title, description, test_category, related_defect_id, preconditions, expected_behavior, execution_command, last_outcome, last_run_at, created_at)
VALUES (
    'TEST-SCENARIO-B',
    'Verify multi-shipment order aggregation prevents cartesian fan-out',
    'Tests order reporting calculation when an order has multiple partial shipments.',
    'REGRESSION',
    'DEF-102',
    'Order ORD-99 with 2 line items and 3 shipment fulfillments',
    'Gross total must exactly match item sum, ignoring duplicate shipment rows.',
    'pytest demo_lab/tests/test_scenario_b_duplicate_aggregation.py -v',
    'PASSED',
    CURRENT_TIMESTAMP,
    TIMESTAMP '2026-10-15 10:00:00'
);

INSERT INTO REGRESSION_TESTS (test_id, title, description, test_category, related_defect_id, preconditions, expected_behavior, execution_command, last_outcome, last_run_at, created_at)
VALUES (
    'TEST-SCENARIO-C',
    'Verify invoice workflow rejects illegal transitions without credit check',
    'Tests state transition guards on high-value invoices.',
    'REGRESSION',
    'DEF-103',
    'Invoice over $50,000 without CREDIT_APPROVED status',
    'Direct transition to ISSUED must fail with ValidationError / 422.',
    'pytest demo_lab/tests/test_scenario_c_invalid_transition.py -v',
    'PASSED',
    CURRENT_TIMESTAMP,
    TIMESTAMP '2026-10-17 14:00:00'
);

INSERT INTO REGRESSION_TESTS (test_id, title, description, test_category, related_defect_id, preconditions, expected_behavior, execution_command, last_outcome, last_run_at, created_at)
VALUES (
    'TEST-SCENARIO-D',
    'Verify atomic transaction rollback on database integrity violation',
    'Tests that an ORA-02291 or constraint failure rolls back all partial writes.',
    'DATABASE_INTEGRATION',
    'DEF-104',
    'Batch containing valid records followed by an invalid parent key',
    'Zero rows committed from the failing batch; complete rollback verified.',
    'pytest demo_lab/tests/test_scenario_d_db_integrity.py -v',
    'PASSED',
    CURRENT_TIMESTAMP,
    TIMESTAMP '2026-10-19 11:00:00'
);

INSERT INTO REGRESSION_TESTS (test_id, title, description, test_category, related_defect_id, preconditions, expected_behavior, execution_command, last_outcome, last_run_at, created_at)
VALUES (
    'TEST-SCENARIO-E',
    'Verify discount calculation respects coupon expiration after optimization',
    'Tests regression prevention on checkout calculation path.',
    'REGRESSION',
    'DEF-105',
    'Expired percentage discount coupon code',
    'Calculation engine must reject coupon with CouponExpiredException.',
    'pytest demo_lab/tests/test_scenario_e_regression_guard.py -v',
    'FAILED',
    CURRENT_TIMESTAMP,
    TIMESTAMP '2026-10-21 09:30:00'
);

-- TEST RUNS
INSERT INTO TEST_RUNS (run_id, test_suite_id, execution_method, command, outcome, passed_count, failed_count, skipped_count, duration_ms, output_summary, environment_meta, related_defect_id, related_release_id, triggered_by, started_at, completed_at)
VALUES (
    'RUN-20261021-01',
    'SUITE-REGRESSION-CORE',
    'AUTOMATED_LOCAL',
    'pytest demo_lab/tests/test_scenario_a_date_boundary.py -v',
    'PASSED',
    3,
    0,
    0,
    142,
    '3 passed in 0.14s. Date boundary half-open interval verified.',
    'Python 3.14.7, Windows, SQLite/Oracle Dialect',
    'DEF-101',
    'REL-2026.1.0',
    'alex.chen',
    TIMESTAMP '2026-10-21 09:00:00',
    TIMESTAMP '2026-10-21 09:00:01'
);

INSERT INTO TEST_RUNS (run_id, test_suite_id, execution_method, command, outcome, passed_count, failed_count, skipped_count, duration_ms, output_summary, environment_meta, related_defect_id, related_release_id, triggered_by, started_at, completed_at)
VALUES (
    'RUN-20261021-02',
    'SUITE-REGRESSION-DISCOUNT',
    'AUTOMATED_LOCAL',
    'pytest demo_lab/tests/test_scenario_e_regression_guard.py -v',
    'FAILED',
    1,
    1,
    0,
    188,
    'FAILED test_expired_coupon_rejected - AssertionError: Expected CouponExpiredException, but discount was applied.',
    'Python 3.14.7, Windows, SQLite/Oracle Dialect',
    'DEF-105',
    'REL-2026.1.0',
    'ci-bot',
    TIMESTAMP '2026-10-21 09:30:00',
    TIMESTAMP '2026-10-21 09:30:01'
);

-- RELEASE CHECKS
INSERT INTO RELEASE_CHECKS (check_id, release_id, check_name, check_category, is_mandatory, status, waiver_reason, verified_at, verified_by, evidence_details)
VALUES (
    'CHK-101',
    'REL-2026.1.0',
    'Mandatory Core Regression Suite Passed',
    'REGRESSION_VERIFICATION',
    1,
    'FAILED',
    NULL,
    CURRENT_TIMESTAMP,
    'ci-pipeline',
    'Run RUN-20261021-02 failed on test_scenario_e_regression_guard.'
);

INSERT INTO RELEASE_CHECKS (check_id, release_id, check_name, check_category, is_mandatory, status, waiver_reason, verified_at, verified_by, evidence_details)
VALUES (
    'CHK-102',
    'REL-2026.1.0',
    'Zero Open Critical/High Blocker Defects',
    'BLOCKER_TRIAGE',
    1,
    'FAILED',
    NULL,
    CURRENT_TIMESTAMP,
    'triage-lead',
    '4 open Critical/High defects remaining (DEF-101, DEF-102, DEF-104, DEF-105).'
);

INSERT INTO RELEASE_CHECKS (check_id, release_id, check_name, check_category, is_mandatory, status, waiver_reason, verified_at, verified_by, evidence_details)
VALUES (
    'CHK-103',
    'REL-2026.1.0',
    'Oracle Database Schema Migration Validated',
    'DATABASE_MIGRATION',
    1,
    'PASSED',
    NULL,
    TIMESTAMP '2026-10-21 08:00:00',
    'dba.team',
    'Migration 001_add_performance_indexes successfully applied and post-check validated.'
);

INSERT INTO RELEASE_CHECKS (check_id, release_id, check_name, check_category, is_mandatory, status, waiver_reason, verified_at, verified_by, evidence_details)
VALUES (
    'CHK-104',
    'REL-2026.1.0',
    'Documented Rollback Procedure Available',
    'ROLLBACK_PLAN',
    1,
    'PASSED',
    NULL,
    TIMESTAMP '2026-10-21 08:30:00',
    'release-engineer',
    'Rollback plan documented in release record with reversible migration scripts.'
);

INSERT INTO RELEASE_CHECKS (check_id, release_id, check_name, check_category, is_mandatory, status, waiver_reason, verified_at, verified_by, evidence_details)
VALUES (
    'CHK-105',
    'REL-2026.1.0',
    'API Security and Sanitization Smoke Tests',
    'SECURITY_SMOKE',
    1,
    'PENDING',
    NULL,
    NULL,
    NULL,
    'Awaiting completion of staging deployment smoke pass.'
);

-- DATABASE CHANGES
INSERT INTO DATABASE_CHANGES (change_id, change_name, change_type, target_schema, sql_script, rollback_script, pre_check_query, post_check_query, status, execution_log, applied_at, applied_by, oracle_object_name)
VALUES (
    'CHG-001',
    '001_add_performance_indexes',
    'INDEX_DDL',
    'TRACEPOINT',
    'CREATE INDEX idx_defects_comp ON DEFECTS (affected_component);',
    'DROP INDEX idx_defects_comp;',
    'SELECT COUNT(*) FROM user_indexes WHERE index_name = ''IDX_DEFECTS_COMP'';',
    'SELECT status FROM user_indexes WHERE index_name = ''IDX_DEFECTS_COMP'';',
    'APPLIED',
    'Pre-check count: 0. Index created in 0.08s. Post-check status: VALID.',
    TIMESTAMP '2026-10-21 08:00:00',
    'alex.chen',
    'IDX_DEFECTS_COMP'
);

INSERT INTO DATABASE_CHANGES (change_id, change_name, change_type, target_schema, sql_script, rollback_script, pre_check_query, post_check_query, status, execution_log, applied_at, applied_by, oracle_object_name)
VALUES (
    'CHG-002',
    '002_add_component_ownership',
    'TABLE_DDL',
    'TRACEPOINT',
    'CREATE TABLE COMPONENT_REGISTRY (component_name VARCHAR2(100) PRIMARY KEY, lead_engineer VARCHAR2(100) NOT NULL, tier VARCHAR2(20) DEFAULT ''CORE'' NOT NULL);',
    'DROP TABLE COMPONENT_REGISTRY;',
    'SELECT COUNT(*) FROM user_tables WHERE table_name = ''COMPONENT_REGISTRY'';',
    'SELECT table_name FROM user_tables WHERE table_name = ''COMPONENT_REGISTRY'';',
    'PENDING',
    'Awaiting DB change validation review before release execution.',
    NULL,
    NULL,
    'COMPONENT_REGISTRY'
);

-- AUDIT LOG
INSERT INTO AUDIT_LOG (audit_id, entity_type, entity_id, action, previous_state, new_state, actor, correlation_id, created_at)
VALUES (
    'AUD-001',
    'DEFECT',
    'DEF-101',
    'CREATED',
    NULL,
    'Status: OPEN, Severity: HIGH',
    'reconciler.bot',
    'TXN-DEF-101-INIT',
    TIMESTAMP '2026-10-12 10:15:00'
);

INSERT INTO AUDIT_LOG (audit_id, entity_type, entity_id, action, previous_state, new_state, actor, correlation_id, created_at)
VALUES (
    'AUD-002',
    'DEFECT',
    'DEF-101',
    'STATUS_TRANSITION',
    'OPEN',
    'REPRODUCED [Reason: Deterministic reproduction with REP-101 fixture]',
    'alex.chen',
    'TXN-DEF-101-REPRO',
    TIMESTAMP '2026-10-12 11:30:00'
);

INSERT INTO AUDIT_LOG (audit_id, entity_type, entity_id, action, previous_state, new_state, actor, correlation_id, created_at)
VALUES (
    'AUD-003',
    'DEFECT',
    'DEF-101',
    'STATUS_TRANSITION',
    'REPRODUCED',
    'INVESTIGATING [Reason: Root cause investigation begun under INV-101]',
    'alex.chen',
    'TXN-DEF-101-INV',
    TIMESTAMP '2026-10-12 11:45:00'
);

INSERT INTO AUDIT_LOG (audit_id, entity_type, entity_id, action, previous_state, new_state, actor, correlation_id, created_at)
VALUES (
    'AUD-004',
    'RELEASE',
    'REL-2026.1.0',
    'READINESS_EVALUATION',
    'Status: DRAFT',
    'BLOCKED [Score: 45%. Blockers: Failed regression test, 4 open critical/high defects]',
    'SYSTEM_GATE_ENGINE',
    'GATE-REL-2026.1.0',
    TIMESTAMP '2026-10-21 09:35:00'
);
