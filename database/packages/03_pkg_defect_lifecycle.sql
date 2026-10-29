-- ============================================================================
-- TRACEPOINT PL/SQL PACKAGE: PKG_DEFECT_LIFECYCLE
-- Provides transactional integrity, state-transition validation, and audit logging.
-- ============================================================================

CREATE OR REPLACE PACKAGE PKG_DEFECT_LIFECYCLE AS
    -- Error codes
    ERR_INVALID_TRANSITION CONSTANT NUMBER := -20001;
    ERR_MISSING_VERIFICATION CONSTANT NUMBER := -20002;
    ERR_DEFECT_NOT_FOUND CONSTANT NUMBER := -20003;

    -- Transitions a defect to a new status with validation and audit logging
    PROCEDURE transition_defect(
        p_defect_id     IN VARCHAR2,
        p_new_status    IN VARCHAR2,
        p_actor         IN VARCHAR2,
        p_reason        IN VARCHAR2,
        p_status_code   OUT NUMBER,
        p_message       OUT VARCHAR2
    );

    -- Checks if transition from current to target status is valid
    FUNCTION is_transition_allowed(
        p_current_status IN VARCHAR2,
        p_target_status  IN VARCHAR2
    ) RETURN BOOLEAN;
END PKG_DEFECT_LIFECYCLE;
/

CREATE OR REPLACE PACKAGE BODY PKG_DEFECT_LIFECYCLE AS

    FUNCTION is_transition_allowed(
        p_current_status IN VARCHAR2,
        p_target_status  IN VARCHAR2
    ) RETURN BOOLEAN IS
    BEGIN
        IF p_current_status = p_target_status THEN
            RETURN TRUE;
        END IF;

        CASE p_current_status
            WHEN 'OPEN' THEN
                RETURN p_target_status IN ('REPRODUCED', 'INVESTIGATING', 'REJECTED', 'DUPLICATE', 'INCONCLUSIVE');
            WHEN 'REPRODUCED' THEN
                RETURN p_target_status IN ('INVESTIGATING', 'FIX_PROPOSED', 'INCONCLUSIVE');
            WHEN 'INVESTIGATING' THEN
                RETURN p_target_status IN ('FIX_PROPOSED', 'INCONCLUSIVE', 'REJECTED', 'REPRODUCED');
            WHEN 'FIX_PROPOSED' THEN
                RETURN p_target_status IN ('VALIDATION_REQUIRED', 'INVESTIGATING');
            WHEN 'VALIDATION_REQUIRED' THEN
                RETURN p_target_status IN ('VERIFIED', 'FIX_PROPOSED', 'INVESTIGATING');
            WHEN 'VERIFIED' THEN
                RETURN p_target_status IN ('CLOSED', 'OPEN');
            WHEN 'INCONCLUSIVE' THEN
                RETURN p_target_status IN ('INVESTIGATING', 'CLOSED', 'OPEN');
            WHEN 'CLOSED' THEN
                RETURN p_target_status IN ('OPEN');
            WHEN 'REJECTED' THEN
                RETURN p_target_status IN ('OPEN');
            WHEN 'DUPLICATE' THEN
                RETURN p_target_status IN ('OPEN');
            ELSE
                RETURN FALSE;
        END CASE;
    END is_transition_allowed;

    PROCEDURE transition_defect(
        p_defect_id     IN VARCHAR2,
        p_new_status    IN VARCHAR2,
        p_actor         IN VARCHAR2,
        p_reason        IN VARCHAR2,
        p_status_code   OUT NUMBER,
        p_message       OUT VARCHAR2
    ) IS
        v_current_status VARCHAR2(30);
        v_verif_status   VARCHAR2(30);
        v_evidence_count NUMBER := 0;
        v_audit_id       VARCHAR2(32);
    BEGIN
        -- 1. Fetch current status
        BEGIN
            SELECT status, verification_status
            INTO v_current_status, v_verif_status
            FROM DEFECTS
            WHERE defect_id = p_defect_id
            FOR UPDATE;
        EXCEPTION
            WHEN NO_DATA_FOUND THEN
                p_status_code := ERR_DEFECT_NOT_FOUND;
                p_message := 'Defect not found: ' || p_defect_id;
                RETURN;
        END;

        -- 2. Validate state machine rule
        IF NOT is_transition_allowed(v_current_status, p_new_status) THEN
            p_status_code := ERR_INVALID_TRANSITION;
            p_message := 'Invalid state transition from ' || v_current_status || ' to ' || p_new_status;
            RETURN;
        END IF;

        -- 3. Transition to VERIFIED requires verification_status = 'VERIFIED'
        IF p_new_status = 'VERIFIED' AND v_verif_status != 'VERIFIED' THEN
            p_status_code := ERR_MISSING_VERIFICATION;
            p_message := 'Cannot mark defect VERIFIED without completed test verification evidence.';
            RETURN;
        END IF;

        -- 4. Update defect record
        UPDATE DEFECTS
        SET status = p_new_status,
            updated_at = CURRENT_TIMESTAMP,
            resolved_at = CASE WHEN p_new_status IN ('CLOSED', 'VERIFIED') THEN CURRENT_TIMESTAMP ELSE resolved_at END
        WHERE defect_id = p_defect_id;

        -- 5. Record immutable audit log
        v_audit_id := 'AUD-' || TO_CHAR(SYSTIMESTAMP, 'YYYYMMDDHH24MISSFF3');
        INSERT INTO AUDIT_LOG (
            audit_id,
            entity_type,
            entity_id,
            action,
            previous_state,
            new_state,
            actor,
            correlation_id,
            created_at
        ) VALUES (
            v_audit_id,
            'DEFECT',
            p_defect_id,
            'STATUS_TRANSITION',
            v_current_status,
            p_new_status || ' [Reason: ' || NVL(p_reason, 'None provided') || ']',
            p_actor,
            'TXN-' || p_defect_id,
            CURRENT_TIMESTAMP
        );

        p_status_code := 0;
        p_message := 'Defect transitioned successfully from ' || v_current_status || ' to ' || p_new_status;
    EXCEPTION
        WHEN OTHERS THEN
            p_status_code := SQLCODE;
            p_message := 'Database error: ' || SQLERRM;
            ROLLBACK;
    END transition_defect;

END PKG_DEFECT_LIFECYCLE;
/
