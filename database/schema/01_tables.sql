-- ============================================================================
-- TRACEPOINT ORACLE SCHEMA DDL
-- Release Reliability & Root Cause Analysis Platform
-- Compatible with Oracle Database Free / 19c / 21c / 23ai
-- ============================================================================

-- 1. DEFECTS TABLE
CREATE TABLE DEFECTS (
    defect_id                    VARCHAR2(32) PRIMARY KEY,
    title                        VARCHAR2(255) NOT NULL,
    description                  CLOB NOT NULL,
    severity                     VARCHAR2(20) NOT NULL,
    priority                     VARCHAR2(20) NOT NULL,
    affected_component           VARCHAR2(100) NOT NULL,
    environment                  VARCHAR2(50) NOT NULL,
    status                       VARCHAR2(30) DEFAULT 'OPEN' NOT NULL,
    reproduction_status          VARCHAR2(30) DEFAULT 'PENDING' NOT NULL,
    expected_behavior            CLOB,
    actual_behavior              CLOB,
    root_cause_explanation       CLOB,
    proposed_correction          CLOB,
    verification_status          VARCHAR2(30) DEFAULT 'UNVERIFIED' NOT NULL,
    assigned_owner               VARCHAR2(100) NOT NULL,
    associated_regression_test_id VARCHAR2(32),
    associated_release_id        VARCHAR2(32),
    created_at                   TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at                   TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    resolved_at                  TIMESTAMP,
    CONSTRAINT chk_defect_severity CHECK (severity IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
    CONSTRAINT chk_defect_priority CHECK (priority IN ('P1', 'P2', 'P3', 'P4')),
    CONSTRAINT chk_defect_status CHECK (status IN (
        'OPEN', 'REPRODUCED', 'INVESTIGATING', 'FIX_PROPOSED',
        'VALIDATION_REQUIRED', 'VERIFIED', 'CLOSED', 'REJECTED',
        'DUPLICATE', 'INCONCLUSIVE'
    )),
    CONSTRAINT chk_repro_status CHECK (reproduction_status IN (
        'PENDING', 'REPRODUCED', 'NOT_REPRODUCED', 'INCONCLUSIVE', 'REQUIRES_MORE_INFO'
    )),
    CONSTRAINT chk_verif_status CHECK (verification_status IN (
        'UNVERIFIED', 'IN_PROGRESS', 'VERIFIED', 'FAILED'
    ))
);

-- 2. REPRODUCTIONS TABLE
CREATE TABLE REPRODUCTIONS (
    reproduction_id              VARCHAR2(32) PRIMARY KEY,
    defect_id                    VARCHAR2(32) NOT NULL,
    preconditions                CLOB,
    environment_info             VARCHAR2(255),
    app_version                  VARCHAR2(50),
    steps_json                   CLOB NOT NULL,
    synthetic_fixture_ref        VARCHAR2(255),
    expected_result              CLOB,
    actual_result                CLOB,
    error_message                CLOB,
    frequency                    VARCHAR2(50) DEFAULT 'ALWAYS' NOT NULL,
    outcome                      VARCHAR2(30) NOT NULL,
    notes                        CLOB,
    executed_by                  VARCHAR2(100) NOT NULL,
    created_at                   TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_repro_defect FOREIGN KEY (defect_id) REFERENCES DEFECTS (defect_id) ON DELETE CASCADE,
    CONSTRAINT chk_repro_outcome CHECK (outcome IN ('REPRODUCED', 'NOT_REPRODUCED', 'INCONCLUSIVE', 'REQUIRES_MORE_INFO')),
    CONSTRAINT chk_repro_freq CHECK (frequency IN ('ALWAYS', 'INTERMITTENT', 'ONCE'))
);

-- 3. INVESTIGATIONS TABLE
CREATE TABLE INVESTIGATIONS (
    investigation_id             VARCHAR2(32) PRIMARY KEY,
    defect_id                    VARCHAR2(32) NOT NULL UNIQUE,
    problem_statement            CLOB NOT NULL,
    observed_symptoms            CLOB NOT NULL,
    initial_hypothesis           CLOB NOT NULL,
    candidate_causes             CLOB,
    confirmed_root_cause         CLOB,
    proposed_correction          CLOB,
    regression_risk              CLOB,
    verification_plan            CLOB,
    final_conclusion             CLOB,
    status                       VARCHAR2(30) DEFAULT 'IN_PROGRESS' NOT NULL,
    lead_investigator            VARCHAR2(100) NOT NULL,
    created_at                   TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at                   TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_inv_defect FOREIGN KEY (defect_id) REFERENCES DEFECTS (defect_id) ON DELETE CASCADE,
    CONSTRAINT chk_inv_status CHECK (status IN ('IN_PROGRESS', 'ROOT_CAUSE_IDENTIFIED', 'VERIFIED', 'INCONCLUSIVE', 'CLOSED'))
);

-- 4. INVESTIGATION_EVENTS TABLE (Audit Timeline)
CREATE TABLE INVESTIGATION_EVENTS (
    event_id                     VARCHAR2(32) PRIMARY KEY,
    investigation_id             VARCHAR2(32) NOT NULL,
    event_type                   VARCHAR2(50) NOT NULL,
    title                        VARCHAR2(255) NOT NULL,
    details                      CLOB,
    actor                        VARCHAR2(100) NOT NULL,
    created_at                   TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_invevt_inv FOREIGN KEY (investigation_id) REFERENCES INVESTIGATIONS (investigation_id) ON DELETE CASCADE
);

-- 5. EVIDENCE TABLE
CREATE TABLE EVIDENCE (
    evidence_id                  VARCHAR2(32) PRIMARY KEY,
    defect_id                    VARCHAR2(32) NOT NULL,
    investigation_id             VARCHAR2(32),
    evidence_type                VARCHAR2(50) NOT NULL,
    title                        VARCHAR2(255) NOT NULL,
    error_code                   VARCHAR2(50),
    sanitized_payload            CLOB NOT NULL,
    component                    VARCHAR2(100),
    environment                  VARCHAR2(50),
    correlation_id               VARCHAR2(100),
    collected_by                 VARCHAR2(100) NOT NULL,
    created_at                   TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_evid_defect FOREIGN KEY (defect_id) REFERENCES DEFECTS (defect_id) ON DELETE CASCADE,
    CONSTRAINT chk_evid_type CHECK (evidence_type IN (
        'ERROR_LOG', 'STACK_TRACE', 'SQL_STATEMENT', 'DB_OBJECT',
        'TEST_OUTPUT', 'CODE_DIFF', 'SYSTEM_METRIC'
    ))
);

-- 6. REGRESSION_TESTS TABLE
CREATE TABLE REGRESSION_TESTS (
    test_id                      VARCHAR2(32) PRIMARY KEY,
    title                        VARCHAR2(255) NOT NULL,
    description                  CLOB NOT NULL,
    test_category                VARCHAR2(30) NOT NULL,
    related_defect_id            VARCHAR2(32),
    preconditions                CLOB,
    expected_behavior            CLOB NOT NULL,
    execution_command            VARCHAR2(255) NOT NULL,
    last_outcome                 VARCHAR2(30) DEFAULT 'NOT_RUN' NOT NULL,
    last_run_at                  TIMESTAMP,
    created_at                   TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_regtest_defect FOREIGN KEY (related_defect_id) REFERENCES DEFECTS (defect_id) ON DELETE SET NULL,
    CONSTRAINT chk_test_category CHECK (test_category IN (
        'UNIT', 'API', 'DATABASE_INTEGRATION', 'REGRESSION', 'END_TO_END'
    )),
    CONSTRAINT chk_test_outcome CHECK (last_outcome IN (
        'PASSED', 'FAILED', 'SKIPPED', 'NOT_RUN'
    ))
);

-- 7. RELEASES TABLE
CREATE TABLE RELEASES (
    release_id                   VARCHAR2(32) PRIMARY KEY,
    version_tag                  VARCHAR2(50) NOT NULL UNIQUE,
    summary                      CLOB NOT NULL,
    status                       VARCHAR2(30) DEFAULT 'DRAFT' NOT NULL,
    rollback_plan                CLOB,
    is_ready                     NUMBER(1) DEFAULT 0 NOT NULL,
    readiness_score              NUMBER DEFAULT 0 NOT NULL,
    created_at                   TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at                   TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    released_at                  TIMESTAMP,
    CONSTRAINT chk_rel_status CHECK (status IN (
        'DRAFT', 'VALIDATION_IN_PROGRESS', 'BLOCKED',
        'READY_FOR_REVIEW', 'APPROVED', 'RELEASED', 'ROLLED_BACK'
    )),
    CONSTRAINT chk_rel_ready CHECK (is_ready IN (0, 1))
);

-- 8. RELEASE_CHECKS TABLE
CREATE TABLE RELEASE_CHECKS (
    check_id                     VARCHAR2(32) PRIMARY KEY,
    release_id                   VARCHAR2(32) NOT NULL,
    check_name                   VARCHAR2(100) NOT NULL,
    check_category               VARCHAR2(50) NOT NULL,
    is_mandatory                 NUMBER(1) DEFAULT 1 NOT NULL,
    status                       VARCHAR2(30) DEFAULT 'PENDING' NOT NULL,
    waiver_reason                CLOB,
    verified_at                  TIMESTAMP,
    verified_by                  VARCHAR2(100),
    evidence_details             CLOB,
    CONSTRAINT fk_relchk_rel FOREIGN KEY (release_id) REFERENCES RELEASES (release_id) ON DELETE CASCADE,
    CONSTRAINT chk_relchk_status CHECK (status IN ('PENDING', 'PASSED', 'FAILED', 'WAIVED')),
    CONSTRAINT chk_relchk_mand CHECK (is_mandatory IN (0, 1))
);

-- 9. TEST_RUNS TABLE
CREATE TABLE TEST_RUNS (
    run_id                       VARCHAR2(32) PRIMARY KEY,
    test_suite_id                VARCHAR2(100) NOT NULL,
    execution_method             VARCHAR2(30) NOT NULL,
    command                      VARCHAR2(255) NOT NULL,
    outcome                      VARCHAR2(30) NOT NULL,
    passed_count                 NUMBER DEFAULT 0 NOT NULL,
    failed_count                 NUMBER DEFAULT 0 NOT NULL,
    skipped_count                NUMBER DEFAULT 0 NOT NULL,
    duration_ms                  NUMBER DEFAULT 0 NOT NULL,
    output_summary               CLOB,
    environment_meta             VARCHAR2(255),
    related_defect_id            VARCHAR2(32),
    related_release_id           VARCHAR2(32),
    triggered_by                 VARCHAR2(100) NOT NULL,
    started_at                   TIMESTAMP NOT NULL,
    completed_at                 TIMESTAMP NOT NULL,
    CONSTRAINT fk_testrun_defect FOREIGN KEY (related_defect_id) REFERENCES DEFECTS (defect_id) ON DELETE SET NULL,
    CONSTRAINT fk_testrun_release FOREIGN KEY (related_release_id) REFERENCES RELEASES (release_id) ON DELETE SET NULL,
    CONSTRAINT chk_testrun_method CHECK (execution_method IN ('AUTOMATED_LOCAL', 'CI_IMPORT', 'MANUAL_VERIFIED')),
    CONSTRAINT chk_testrun_outcome CHECK (outcome IN ('PASSED', 'FAILED', 'ERROR'))
);

-- 10. DATABASE_CHANGES TABLE
CREATE TABLE DATABASE_CHANGES (
    change_id                    VARCHAR2(32) PRIMARY KEY,
    change_name                  VARCHAR2(100) NOT NULL,
    change_type                  VARCHAR2(50) NOT NULL,
    target_schema                VARCHAR2(50) NOT NULL,
    sql_script                   CLOB NOT NULL,
    rollback_script              CLOB,
    pre_check_query              CLOB,
    post_check_query             CLOB,
    status                       VARCHAR2(30) DEFAULT 'PENDING' NOT NULL,
    execution_log                CLOB,
    applied_at                   TIMESTAMP,
    applied_by                   VARCHAR2(100),
    oracle_object_name           VARCHAR2(100),
    CONSTRAINT chk_dbchange_status CHECK (status IN ('PENDING', 'VALIDATED', 'APPLIED', 'FAILED', 'ROLLED_BACK')),
    CONSTRAINT chk_dbchange_type CHECK (change_type IN (
        'TABLE_DDL', 'INDEX_DDL', 'CONSTRAINT_DDL', 'PLSQL_PACKAGE', 'PLSQL_PROCEDURE', 'DATA_MIGRATION'
    ))
);

-- 11. AUDIT_LOG TABLE (Immutable Ledger)
CREATE TABLE AUDIT_LOG (
    audit_id                     VARCHAR2(32) PRIMARY KEY,
    entity_type                  VARCHAR2(50) NOT NULL,
    entity_id                    VARCHAR2(100) NOT NULL,
    action                       VARCHAR2(50) NOT NULL,
    previous_state               CLOB,
    new_state                    CLOB,
    actor                        VARCHAR2(100) NOT NULL,
    correlation_id               VARCHAR2(100),
    created_at                   TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- INDEXES FOR QUERY OPTIMIZATION
CREATE INDEX idx_defects_status ON DEFECTS (status);
CREATE INDEX idx_defects_severity ON DEFECTS (severity);
CREATE INDEX idx_defects_release ON DEFECTS (associated_release_id);
CREATE INDEX idx_inv_defect ON INVESTIGATIONS (defect_id);
CREATE INDEX idx_evidence_defect ON EVIDENCE (defect_id);
CREATE INDEX idx_testruns_release ON TEST_RUNS (related_release_id);
CREATE INDEX idx_audit_entity ON AUDIT_LOG (entity_type, entity_id);
