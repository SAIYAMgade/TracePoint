export type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
export type Priority = 'P1' | 'P2' | 'P3' | 'P4';
export type DefectStatus =
  | 'OPEN'
  | 'REPRODUCED'
  | 'INVESTIGATING'
  | 'FIX_PROPOSED'
  | 'VALIDATION_REQUIRED'
  | 'VERIFIED'
  | 'CLOSED'
  | 'REJECTED'
  | 'DUPLICATE'
  | 'INCONCLUSIVE';

export type ReproductionStatus =
  | 'PENDING'
  | 'REPRODUCED'
  | 'NOT_REPRODUCED'
  | 'INCONCLUSIVE'
  | 'REQUIRES_MORE_INFO';

export type VerificationStatus =
  | 'UNVERIFIED'
  | 'IN_PROGRESS'
  | 'VERIFIED'
  | 'FAILED';

export interface Defect {
  defect_id: string;
  title: string;
  description: string;
  severity: Severity;
  priority: Priority;
  affected_component: string;
  environment: string;
  status: DefectStatus;
  reproduction_status: ReproductionStatus;
  expected_behavior?: string;
  actual_behavior?: string;
  root_cause_explanation?: string;
  proposed_correction?: string;
  verification_status: VerificationStatus;
  assigned_owner: string;
  associated_regression_test_id?: string;
  associated_release_id?: string;
  created_at: string;
  updated_at: string;
  resolved_at?: string;
}

export interface InvestigationEvent {
  event_id: string;
  investigation_id: string;
  event_type: string;
  title: string;
  details?: string;
  actor: string;
  created_at: string;
}

export interface Investigation {
  investigation_id: string;
  defect_id: string;
  problem_statement: string;
  observed_symptoms: string;
  initial_hypothesis: string;
  candidate_causes?: string;
  confirmed_root_cause?: string;
  proposed_correction?: string;
  regression_risk?: string;
  verification_plan?: string;
  final_conclusion?: string;
  status: 'IN_PROGRESS' | 'ROOT_CAUSE_IDENTIFIED' | 'VERIFIED' | 'INCONCLUSIVE' | 'CLOSED';
  lead_investigator: string;
  created_at: string;
  updated_at: string;
  events?: InvestigationEvent[];
}

export interface Evidence {
  evidence_id: string;
  defect_id: string;
  investigation_id?: string;
  evidence_type: 'ERROR_LOG' | 'STACK_TRACE' | 'SQL_STATEMENT' | 'DB_OBJECT' | 'TEST_OUTPUT' | 'CODE_DIFF' | 'SYSTEM_METRIC';
  title: string;
  error_code?: string;
  sanitized_payload: string;
  component?: string;
  environment?: string;
  correlation_id?: string;
  collected_by: string;
  created_at: string;
}

export interface Reproduction {
  reproduction_id: string;
  defect_id: string;
  preconditions?: string;
  environment_info?: string;
  app_version?: string;
  steps: string[];
  synthetic_fixture_ref?: string;
  expected_result?: string;
  actual_result?: string;
  error_message?: string;
  frequency: 'ALWAYS' | 'INTERMITTENT' | 'ONCE';
  outcome: 'REPRODUCED' | 'NOT_REPRODUCED' | 'INCONCLUSIVE' | 'REQUIRES_MORE_INFO';
  notes?: string;
  executed_by: string;
  created_at: string;
}

export interface RegressionTest {
  test_id: string;
  title: string;
  description: string;
  test_category: 'UNIT' | 'API' | 'DATABASE_INTEGRATION' | 'REGRESSION' | 'END_TO_END';
  related_defect_id?: string;
  preconditions?: string;
  expected_behavior: string;
  execution_command: string;
  last_outcome: 'PASSED' | 'FAILED' | 'SKIPPED' | 'NOT_RUN';
  last_run_at?: string;
  created_at: string;
}

export interface TestRun {
  run_id: string;
  test_suite_id: string;
  execution_method: string;
  command: string;
  outcome: 'PASSED' | 'FAILED' | 'ERROR';
  passed_count: number;
  failed_count: number;
  skipped_count: number;
  duration_ms: number;
  output_summary?: string;
  environment_meta?: string;
  related_defect_id?: string;
  related_release_id?: string;
  triggered_by: string;
  started_at: string;
  completed_at: string;
}

export interface ReleaseCheck {
  check_id: string;
  release_id: string;
  check_name: string;
  check_category: string;
  is_mandatory: boolean;
  status: 'PENDING' | 'PASSED' | 'FAILED' | 'WAIVED';
  waiver_reason?: string;
  verified_at?: string;
  verified_by?: string;
  evidence_details?: string;
}

export interface Release {
  release_id: string;
  version_tag: string;
  summary: string;
  status: 'DRAFT' | 'VALIDATION_IN_PROGRESS' | 'BLOCKED' | 'READY_FOR_REVIEW' | 'APPROVED' | 'RELEASED' | 'ROLLED_BACK';
  rollback_plan?: string;
  is_ready: boolean;
  readiness_score: number;
  created_at: string;
  updated_at: string;
  released_at?: string;
  checks?: ReleaseCheck[];
}

export interface DatabaseChange {
  change_id: string;
  change_name: string;
  change_type: string;
  target_schema: string;
  sql_script: string;
  rollback_script?: string;
  pre_check_query?: string;
  post_check_query?: string;
  status: 'PENDING' | 'VALIDATED' | 'APPLIED' | 'FAILED' | 'ROLLED_BACK';
  execution_log?: string;
  applied_at?: string;
  applied_by?: string;
  oracle_object_name?: string;
}

export interface AuditLogItem {
  audit_id: string;
  entity_type: string;
  entity_id: string;
  action: string;
  previous_state?: string;
  new_state?: string;
  actor: string;
  correlation_id?: string;
  created_at: string;
}

export interface DashboardMetrics {
  open_defects_by_severity: Record<string, number>;
  defects_awaiting_reproduction: number;
  investigations_without_root_cause: number;
  fixes_awaiting_verification: number;
  failed_regression_tests: number;
  releases_blocked: number;
  reopened_defects_count: number;
  avg_resolution_hours?: number;
  total_active_defects: number;
  total_verified_defects: number;
}

export interface SystemHealth {
  status: string;
  service: string;
  environment: string;
  database: {
    configured_engine: string;
    active_dialect: string;
    is_oracle: boolean;
    driver_available: boolean;
    connection_status: string;
    server_version: string;
    fallback_notice?: string;
    verified_oracle_capabilities: string[];
    defect_records_count?: number;
  };
  tracepoint_lab_active: boolean;
  supported_test_runner: string;
}
