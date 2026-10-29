-- ============================================================================
-- TRACEPOINT ORACLE VIEWS & ANALYTIC REPORTS
-- ============================================================================

-- 1. Open defects grouped by severity
CREATE OR REPLACE VIEW V_OPEN_DEFECTS_BY_SEVERITY AS
SELECT 
    severity,
    COUNT(*) AS defect_count,
    COUNT(CASE WHEN reproduction_status = 'PENDING' THEN 1 END) AS awaiting_repro_count,
    COUNT(CASE WHEN verification_status = 'UNVERIFIED' THEN 1 END) AS unverified_count
FROM DEFECTS
WHERE status NOT IN ('CLOSED', 'REJECTED')
GROUP BY severity;

-- 2. Defects awaiting verification
CREATE OR REPLACE VIEW V_DEFECTS_AWAITING_VERIFICATION AS
SELECT 
    d.defect_id,
    d.title,
    d.severity,
    d.priority,
    d.affected_component,
    d.status,
    d.proposed_correction,
    d.associated_regression_test_id,
    i.investigation_id,
    i.lead_investigator,
    d.updated_at
FROM DEFECTS d
LEFT JOIN INVESTIGATIONS i ON d.defect_id = i.defect_id
WHERE d.status IN ('FIX_PROPOSED', 'VALIDATION_REQUIRED')
   OR (d.status = 'OPEN' AND d.proposed_correction IS NOT NULL);

-- 3. Investigations without a confirmed root cause
CREATE OR REPLACE VIEW V_UNCONFIRMED_INVESTIGATIONS AS
SELECT 
    i.investigation_id,
    i.defect_id,
    d.title AS defect_title,
    d.severity,
    i.problem_statement,
    i.initial_hypothesis,
    i.lead_investigator,
    i.created_at,
    (SELECT COUNT(*) FROM EVIDENCE e WHERE e.investigation_id = i.investigation_id) AS evidence_count,
    (SELECT COUNT(*) FROM INVESTIGATION_EVENTS ie WHERE ie.investigation_id = i.investigation_id) AS event_count
FROM INVESTIGATIONS i
JOIN DEFECTS d ON i.defect_id = d.defect_id
WHERE i.confirmed_root_cause IS NULL
  AND d.status NOT IN ('CLOSED', 'REJECTED');

-- 4. Failed regression tests by release
CREATE OR REPLACE VIEW V_FAILED_REGRESSION_TESTS AS
SELECT 
    rt.test_id,
    rt.title,
    rt.test_category,
    rt.related_defect_id,
    d.title AS defect_title,
    tr.run_id,
    tr.related_release_id,
    tr.command,
    tr.output_summary,
    tr.completed_at
FROM REGRESSION_TESTS rt
JOIN TEST_RUNS tr ON rt.execution_command = tr.command
LEFT JOIN DEFECTS d ON rt.related_defect_id = d.defect_id
WHERE tr.outcome = 'FAILED'
   OR rt.last_outcome = 'FAILED';

-- 5. Releases blocked by missing or failed checks
CREATE OR REPLACE VIEW V_BLOCKED_RELEASES AS
SELECT 
    r.release_id,
    r.version_tag,
    r.status,
    COUNT(rc.check_id) AS total_checks,
    COUNT(CASE WHEN rc.is_mandatory = 1 AND rc.status = 'FAILED' THEN 1 END) AS mandatory_failed_count,
    COUNT(CASE WHEN rc.is_mandatory = 1 AND rc.status = 'PENDING' THEN 1 END) AS mandatory_pending_count,
    COUNT(CASE WHEN rc.status = 'PASSED' THEN 1 END) AS passed_count,
    r.readiness_score,
    r.rollback_plan
FROM RELEASES r
LEFT JOIN RELEASE_CHECKS rc ON r.release_id = rc.release_id
GROUP BY r.release_id, r.version_tag, r.status, r.readiness_score, r.rollback_plan;

-- 6. Defect resolution metrics (time from creation to resolution)
CREATE OR REPLACE VIEW V_DEFECT_RESOLUTION_METRICS AS
SELECT 
    severity,
    COUNT(*) AS total_resolved,
    ROUND(AVG((CAST(resolved_at AS DATE) - CAST(created_at AS DATE)) * 24), 2) AS avg_resolution_hours,
    ROUND(MIN((CAST(resolved_at AS DATE) - CAST(created_at AS DATE)) * 24), 2) AS min_resolution_hours,
    ROUND(MAX((CAST(resolved_at AS DATE) - CAST(created_at AS DATE)) * 24), 2) AS max_resolution_hours
FROM DEFECTS
WHERE status = 'CLOSED' 
  AND resolved_at IS NOT NULL
GROUP BY severity;

-- 7. Reopened defect analysis
CREATE OR REPLACE VIEW V_REOPENED_DEFECT_ANALYSIS AS
SELECT 
    a.entity_id AS defect_id,
    d.title,
    d.severity,
    d.affected_component,
    COUNT(*) AS reopen_count,
    MAX(a.created_at) AS last_reopened_at
FROM AUDIT_LOG a
JOIN DEFECTS d ON a.entity_id = d.defect_id
WHERE a.entity_type = 'DEFECT'
  AND a.action = 'STATUS_CHANGE'
  AND a.previous_state LIKE '%CLOSED%'
  AND a.new_state LIKE '%OPEN%'
GROUP BY a.entity_id, d.title, d.severity, d.affected_component;

-- 8. Database change validation status
CREATE OR REPLACE VIEW V_DB_CHANGE_STATUS AS
SELECT 
    change_type,
    status,
    COUNT(*) AS change_count,
    MAX(applied_at) AS last_applied_at
FROM DATABASE_CHANGES
GROUP BY change_type, status;
