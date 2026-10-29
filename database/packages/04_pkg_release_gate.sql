-- ============================================================================
-- TRACEPOINT PL/SQL PACKAGE: PKG_RELEASE_GATE
-- Evaluates objective release criteria against persisted test runs and checks.
-- ============================================================================

CREATE OR REPLACE PACKAGE PKG_RELEASE_GATE AS
    -- Evaluates whether a release meets all readiness criteria
    PROCEDURE evaluate_readiness(
        p_release_id    IN VARCHAR2,
        p_is_ready      OUT NUMBER,
        p_score         OUT NUMBER,
        p_blockers      OUT VARCHAR2
    );
END PKG_RELEASE_GATE;
/

CREATE OR REPLACE PACKAGE BODY PKG_RELEASE_GATE AS

    PROCEDURE evaluate_readiness(
        p_release_id    IN VARCHAR2,
        p_is_ready      OUT NUMBER,
        p_score         OUT NUMBER,
        p_blockers      OUT VARCHAR2
    ) IS
        v_total_checks     NUMBER := 0;
        v_passed_checks    NUMBER := 0;
        v_failed_mand      NUMBER := 0;
        v_pending_mand     NUMBER := 0;
        v_open_blockers    NUMBER := 0;
        v_failed_reg_tests NUMBER := 0;
        v_failed_db_chgs   NUMBER := 0;
        v_blocker_list     VARCHAR2(4000) := '';
    BEGIN
        -- 1. Check mandatory release checks
        SELECT 
            COUNT(*),
            COUNT(CASE WHEN status IN ('PASSED', 'WAIVED') THEN 1 END),
            COUNT(CASE WHEN is_mandatory = 1 AND status = 'FAILED' THEN 1 END),
            COUNT(CASE WHEN is_mandatory = 1 AND status = 'PENDING' THEN 1 END)
        INTO v_total_checks, v_passed_checks, v_failed_mand, v_pending_mand
        FROM RELEASE_CHECKS
        WHERE release_id = p_release_id;

        IF v_failed_mand > 0 THEN
            v_blocker_list := v_blocker_list || '[' || v_failed_mand || ' mandatory release check(s) FAILED] ';
        END IF;

        IF v_pending_mand > 0 THEN
            v_blocker_list := v_blocker_list || '[' || v_pending_mand || ' mandatory release check(s) PENDING] ';
        END IF;

        -- 2. Check for unresolved Critical or High defects tied to this release
        SELECT COUNT(*)
        INTO v_open_blockers
        FROM DEFECTS
        WHERE associated_release_id = p_release_id
          AND severity IN ('CRITICAL', 'HIGH')
          AND status NOT IN ('CLOSED', 'VERIFIED');

        IF v_open_blockers > 0 THEN
            v_blocker_list := v_blocker_list || '[' || v_open_blockers || ' open Critical/High defect(s) unresolved] ';
        END IF;

        -- 3. Check for any regression tests tied to this release that failed
        SELECT COUNT(*)
        INTO v_failed_reg_tests
        FROM TEST_RUNS
        WHERE related_release_id = p_release_id
          AND outcome = 'FAILED';

        IF v_failed_reg_tests > 0 THEN
            v_blocker_list := v_blocker_list || '[' || v_failed_reg_tests || ' failed test run(s)] ';
        END IF;

        -- 4. Calculate score
        IF v_total_checks > 0 THEN
            p_score := ROUND((v_passed_checks / v_total_checks) * 100);
        ELSE
            p_score := 0;
        END IF;

        -- 5. Determine overall readiness
        IF v_failed_mand = 0 AND v_pending_mand = 0 AND v_open_blockers = 0 AND v_failed_reg_tests = 0 AND v_total_checks > 0 THEN
            p_is_ready := 1;
            p_blockers := 'None. All release gates satisfied.';
            
            UPDATE RELEASES
            SET is_ready = 1,
                readiness_score = p_score,
                status = CASE WHEN status = 'DRAFT' THEN 'READY_FOR_REVIEW' ELSE status END,
                updated_at = CURRENT_TIMESTAMP
            WHERE release_id = p_release_id;
        ELSE
            p_is_ready := 0;
            p_blockers := TRIM(v_blocker_list);

            UPDATE RELEASES
            SET is_ready = 0,
                readiness_score = p_score,
                status = 'BLOCKED',
                updated_at = CURRENT_TIMESTAMP
            WHERE release_id = p_release_id;
        END IF;

        -- 6. Record audit
        INSERT INTO AUDIT_LOG (
            audit_id, entity_type, entity_id, action,
            previous_state, new_state, actor, correlation_id, created_at
        ) VALUES (
            'AUD-' || TO_CHAR(SYSTIMESTAMP, 'YYYYMMDDHH24MISSFF3'),
            'RELEASE',
            p_release_id,
            'READINESS_EVALUATION',
            'Score: ' || p_score || '%, Ready: ' || p_is_ready,
            p_blockers,
            'SYSTEM_GATE_ENGINE',
            'GATE-' || p_release_id,
            CURRENT_TIMESTAMP
        );

    END evaluate_readiness;

END PKG_RELEASE_GATE;
/
