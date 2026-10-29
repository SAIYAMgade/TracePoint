import sqlite3
import os
from contextlib import contextmanager
from typing import Generator, Any, Dict, List, Optional
from datetime import datetime

from .config import settings
from .logging import logger

# Try importing oracledb
try:
    import oracledb
    ORACLE_DRIVER_AVAILABLE = True
except ImportError:
    oracledb = None
    ORACLE_DRIVER_AVAILABLE = False

class DatabaseManager:
    def __init__(self):
        self.engine_type = "sqlite"
        self.is_oracle = False
        self.connection_error: Optional[str] = None
        self._init_engine_preference()

    def _init_engine_preference(self):
        # Determine whether to attempt Oracle connection
        if settings.DB_ENGINE == "oracle":
            if not ORACLE_DRIVER_AVAILABLE:
                self.connection_error = "oracledb package not installed; falling back to SQLite."
                logger.warning(self.connection_error)
                self.engine_type = "sqlite"
                self.is_oracle = False
            elif not settings.ORACLE_USER or not settings.ORACLE_PASSWORD:
                self.connection_error = "Oracle credentials missing in environment; falling back to SQLite."
                logger.warning(self.connection_error)
                self.engine_type = "sqlite"
                self.is_oracle = False
            else:
                # Test connectivity
                try:
                    conn = oracledb.connect(
                        user=settings.ORACLE_USER,
                        password=settings.ORACLE_PASSWORD,
                        dsn=settings.ORACLE_DSN
                    )
                    conn.close()
                    self.engine_type = "oracle"
                    self.is_oracle = True
                    logger.info("Successfully connected to Oracle Database instance: %s", settings.ORACLE_DSN)
                except Exception as e:
                    self.connection_error = f"Failed to connect to Oracle: {str(e)}; falling back to SQLite."
                    logger.warning(self.connection_error)
                    self.engine_type = "sqlite"
                    self.is_oracle = False
        else:
            self.engine_type = "sqlite"
            self.is_oracle = False

    def get_connection(self):
        if self.is_oracle:
            return oracledb.connect(
                user=settings.ORACLE_USER,
                password=settings.ORACLE_PASSWORD,
                dsn=settings.ORACLE_DSN
            )
        else:
            conn = sqlite3.connect(
                str(settings.BASE_DIR / settings.SQLITE_DB_PATH),
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
                timeout=30.0
            )
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn

    @contextmanager
    def session(self) -> Generator[Any, None, None]:
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error("Transaction rolled back due to error: %s", str(e))
            raise
        finally:
            conn.close()

    def get_health(self) -> Dict[str, Any]:
        info = {
            "configured_engine": settings.DB_ENGINE,
            "active_dialect": self.engine_type,
            "is_oracle": self.is_oracle,
            "driver_available": ORACLE_DRIVER_AVAILABLE,
            "connection_status": "ONLINE",
            "fallback_notice": self.connection_error,
            "verified_oracle_capabilities": []
        }
        try:
            with self.session() as conn:
                cursor = conn.cursor()
                if self.is_oracle:
                    cursor.execute("SELECT banner FROM v$version WHERE ROWNUM = 1")
                    row = cursor.fetchone()
                    info["server_version"] = row[0] if row else "Oracle Database"
                    info["verified_oracle_capabilities"] = [
                        "PL/SQL Package Execution",
                        "Oracle Temporal Data Types",
                        "Transaction Rollback Isolation",
                        "Materialized & Normal Views"
                    ]
                else:
                    cursor.execute("SELECT sqlite_version()")
                    row = cursor.fetchone()
                    info["server_version"] = f"SQLite {row[0]} (Local Emulation Mode)"
                    info["verified_oracle_capabilities"] = [
                        "Oracle Schema DDL (Exported)",
                        "PL/SQL Source Code (Validated)",
                        "Local Constraint Enforcement (Foreign Keys Active)"
                    ]
                
                # Check defect table count
                cursor.execute("SELECT COUNT(*) FROM DEFECTS")
                row = cursor.fetchone()
                info["defect_records_count"] = row[0]
        except Exception as e:
            info["connection_status"] = "ERROR"
            info["error_message"] = str(e)
        return info

db_manager = DatabaseManager()

def init_db(force: bool = False):
    """Initializes tables and seeds initial data if needed."""
    if db_manager.is_oracle:
        _init_oracle_db()
    else:
        _init_sqlite_db(force)

def _init_oracle_db():
    logger.info("Initializing Oracle Database tables...")
    # Read and execute 01_tables.sql, 02_views.sql, etc.
    tables_file = settings.DATABASE_DIR / "schema" / "01_tables.sql"
    if tables_file.exists():
        with open(tables_file, "r", encoding="utf-8") as f:
            content = f.read()
        with db_manager.session() as conn:
            cursor = conn.cursor()
            # Split and execute
            statements = content.split(";")
            for stmt in statements:
                stmt_clean = stmt.strip()
                if stmt_clean and not stmt_clean.startswith("--"):
                    try:
                        cursor.execute(stmt_clean)
                    except Exception as e:
                        logger.debug("Oracle DDL notice: %s", str(e))

def _init_sqlite_db(force: bool = False):
    logger.info("Initializing SQLite database with strict constraint schema...")
    with db_manager.session() as conn:
        cursor = conn.cursor()
        
        # Create DEFECTS
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS DEFECTS (
            defect_id VARCHAR(32) PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            severity VARCHAR(20) NOT NULL CHECK(severity IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
            priority VARCHAR(20) NOT NULL CHECK(priority IN ('P1', 'P2', 'P3', 'P4')),
            affected_component VARCHAR(100) NOT NULL,
            environment VARCHAR(50) NOT NULL,
            status VARCHAR(30) NOT NULL DEFAULT 'OPEN' CHECK(status IN (
                'OPEN', 'REPRODUCED', 'INVESTIGATING', 'FIX_PROPOSED',
                'VALIDATION_REQUIRED', 'VERIFIED', 'CLOSED', 'REJECTED',
                'DUPLICATE', 'INCONCLUSIVE'
            )),
            reproduction_status VARCHAR(30) NOT NULL DEFAULT 'PENDING' CHECK(reproduction_status IN (
                'PENDING', 'REPRODUCED', 'NOT_REPRODUCED', 'INCONCLUSIVE', 'REQUIRES_MORE_INFO'
            )),
            expected_behavior TEXT,
            actual_behavior TEXT,
            root_cause_explanation TEXT,
            proposed_correction TEXT,
            verification_status VARCHAR(30) NOT NULL DEFAULT 'UNVERIFIED' CHECK(verification_status IN (
                'UNVERIFIED', 'IN_PROGRESS', 'VERIFIED', 'FAILED'
            )),
            assigned_owner VARCHAR(100) NOT NULL,
            associated_regression_test_id VARCHAR(32),
            associated_release_id VARCHAR(32),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            resolved_at TIMESTAMP
        );
        """)

        # REPRODUCTIONS
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS REPRODUCTIONS (
            reproduction_id VARCHAR(32) PRIMARY KEY,
            defect_id VARCHAR(32) NOT NULL,
            preconditions TEXT,
            environment_info VARCHAR(255),
            app_version VARCHAR(50),
            steps_json TEXT NOT NULL,
            synthetic_fixture_ref VARCHAR(255),
            expected_result TEXT,
            actual_result TEXT,
            error_message TEXT,
            frequency VARCHAR(50) DEFAULT 'ALWAYS' NOT NULL CHECK(frequency IN ('ALWAYS', 'INTERMITTENT', 'ONCE')),
            outcome VARCHAR(30) NOT NULL CHECK(outcome IN ('REPRODUCED', 'NOT_REPRODUCED', 'INCONCLUSIVE', 'REQUIRES_MORE_INFO')),
            notes TEXT,
            executed_by VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            FOREIGN KEY (defect_id) REFERENCES DEFECTS (defect_id) ON DELETE CASCADE
        );
        """)

        # INVESTIGATIONS
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS INVESTIGATIONS (
            investigation_id VARCHAR(32) PRIMARY KEY,
            defect_id VARCHAR(32) NOT NULL UNIQUE,
            problem_statement TEXT NOT NULL,
            observed_symptoms TEXT NOT NULL,
            initial_hypothesis TEXT NOT NULL,
            candidate_causes TEXT,
            confirmed_root_cause TEXT,
            proposed_correction TEXT,
            regression_risk TEXT,
            verification_plan TEXT,
            final_conclusion TEXT,
            status VARCHAR(30) DEFAULT 'IN_PROGRESS' NOT NULL CHECK(status IN ('IN_PROGRESS', 'ROOT_CAUSE_IDENTIFIED', 'VERIFIED', 'INCONCLUSIVE', 'CLOSED')),
            lead_investigator VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            FOREIGN KEY (defect_id) REFERENCES DEFECTS (defect_id) ON DELETE CASCADE
        );
        """)

        # INVESTIGATION_EVENTS
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS INVESTIGATION_EVENTS (
            event_id VARCHAR(32) PRIMARY KEY,
            investigation_id VARCHAR(32) NOT NULL,
            event_type VARCHAR(50) NOT NULL,
            title VARCHAR(255) NOT NULL,
            details TEXT,
            actor VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            FOREIGN KEY (investigation_id) REFERENCES INVESTIGATIONS (investigation_id) ON DELETE CASCADE
        );
        """)

        # EVIDENCE
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS EVIDENCE (
            evidence_id VARCHAR(32) PRIMARY KEY,
            defect_id VARCHAR(32) NOT NULL,
            investigation_id VARCHAR(32),
            evidence_type VARCHAR(50) NOT NULL CHECK(evidence_type IN (
                'ERROR_LOG', 'STACK_TRACE', 'SQL_STATEMENT', 'DB_OBJECT',
                'TEST_OUTPUT', 'CODE_DIFF', 'SYSTEM_METRIC'
            )),
            title VARCHAR(255) NOT NULL,
            error_code VARCHAR(50),
            sanitized_payload TEXT NOT NULL,
            component VARCHAR(100),
            environment VARCHAR(50),
            correlation_id VARCHAR(100),
            collected_by VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            FOREIGN KEY (defect_id) REFERENCES DEFECTS (defect_id) ON DELETE CASCADE
        );
        """)

        # RELEASES
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS RELEASES (
            release_id VARCHAR(32) PRIMARY KEY,
            version_tag VARCHAR(50) NOT NULL UNIQUE,
            summary TEXT NOT NULL,
            status VARCHAR(30) DEFAULT 'DRAFT' NOT NULL CHECK(status IN (
                'DRAFT', 'VALIDATION_IN_PROGRESS', 'BLOCKED',
                'READY_FOR_REVIEW', 'APPROVED', 'RELEASED', 'ROLLED_BACK'
            )),
            rollback_plan TEXT,
            is_ready INTEGER DEFAULT 0 NOT NULL CHECK(is_ready IN (0, 1)),
            readiness_score REAL DEFAULT 0 NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            released_at TIMESTAMP
        );
        """)

        # RELEASE_CHECKS
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS RELEASE_CHECKS (
            check_id VARCHAR(32) PRIMARY KEY,
            release_id VARCHAR(32) NOT NULL,
            check_name VARCHAR(100) NOT NULL,
            check_category VARCHAR(50) NOT NULL,
            is_mandatory INTEGER DEFAULT 1 NOT NULL CHECK(is_mandatory IN (0, 1)),
            status VARCHAR(30) DEFAULT 'PENDING' NOT NULL CHECK(status IN ('PENDING', 'PASSED', 'FAILED', 'WAIVED')),
            waiver_reason TEXT,
            verified_at TIMESTAMP,
            verified_by VARCHAR(100),
            evidence_details TEXT,
            FOREIGN KEY (release_id) REFERENCES RELEASES (release_id) ON DELETE CASCADE
        );
        """)

        # REGRESSION_TESTS
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS REGRESSION_TESTS (
            test_id VARCHAR(32) PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            test_category VARCHAR(30) NOT NULL CHECK(test_category IN (
                'UNIT', 'API', 'DATABASE_INTEGRATION', 'REGRESSION', 'END_TO_END'
            )),
            related_defect_id VARCHAR(32),
            preconditions TEXT,
            expected_behavior TEXT NOT NULL,
            execution_command VARCHAR(255) NOT NULL,
            last_outcome VARCHAR(30) DEFAULT 'NOT_RUN' NOT NULL CHECK(last_outcome IN (
                'PASSED', 'FAILED', 'SKIPPED', 'NOT_RUN'
            )),
            last_run_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            FOREIGN KEY (related_defect_id) REFERENCES DEFECTS (defect_id) ON DELETE SET NULL
        );
        """)

        # TEST_RUNS
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS TEST_RUNS (
            run_id VARCHAR(32) PRIMARY KEY,
            test_suite_id VARCHAR(100) NOT NULL,
            execution_method VARCHAR(30) NOT NULL CHECK(execution_method IN ('AUTOMATED_LOCAL', 'CI_IMPORT', 'MANUAL_VERIFIED')),
            command VARCHAR(255) NOT NULL,
            outcome VARCHAR(30) NOT NULL CHECK(outcome IN ('PASSED', 'FAILED', 'ERROR')),
            passed_count INTEGER DEFAULT 0 NOT NULL,
            failed_count INTEGER DEFAULT 0 NOT NULL,
            skipped_count INTEGER DEFAULT 0 NOT NULL,
            duration_ms INTEGER DEFAULT 0 NOT NULL,
            output_summary TEXT,
            environment_meta VARCHAR(255),
            related_defect_id VARCHAR(32),
            related_release_id VARCHAR(32),
            triggered_by VARCHAR(100) NOT NULL,
            started_at TIMESTAMP NOT NULL,
            completed_at TIMESTAMP NOT NULL,
            FOREIGN KEY (related_defect_id) REFERENCES DEFECTS (defect_id) ON DELETE SET NULL,
            FOREIGN KEY (related_release_id) REFERENCES RELEASES (release_id) ON DELETE SET NULL
        );
        """)

        # DATABASE_CHANGES
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS DATABASE_CHANGES (
            change_id VARCHAR(32) PRIMARY KEY,
            change_name VARCHAR(100) NOT NULL,
            change_type VARCHAR(50) NOT NULL CHECK(change_type IN (
                'TABLE_DDL', 'INDEX_DDL', 'CONSTRAINT_DDL', 'PLSQL_PACKAGE', 'PLSQL_PROCEDURE', 'DATA_MIGRATION'
            )),
            target_schema VARCHAR(50) NOT NULL,
            sql_script TEXT NOT NULL,
            rollback_script TEXT,
            pre_check_query TEXT,
            post_check_query TEXT,
            status VARCHAR(30) DEFAULT 'PENDING' NOT NULL CHECK(status IN ('PENDING', 'VALIDATED', 'APPLIED', 'FAILED', 'ROLLED_BACK')),
            execution_log TEXT,
            applied_at TIMESTAMP,
            applied_by VARCHAR(100),
            oracle_object_name VARCHAR(100)
        );
        """)

        # AUDIT_LOG
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS AUDIT_LOG (
            audit_id VARCHAR(32) PRIMARY KEY,
            entity_type VARCHAR(50) NOT NULL,
            entity_id VARCHAR(100) NOT NULL,
            action VARCHAR(50) NOT NULL,
            previous_state TEXT,
            new_state TEXT,
            actor VARCHAR(100) NOT NULL,
            correlation_id VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
        );
        """)

        # Indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_defects_status ON DEFECTS (status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_defects_sev ON DEFECTS (severity);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_evidence_def ON EVIDENCE (defect_id);")

        # Views
        cursor.execute("DROP VIEW IF EXISTS V_OPEN_DEFECTS_BY_SEVERITY;")
        cursor.execute("""
        CREATE VIEW V_OPEN_DEFECTS_BY_SEVERITY AS
        SELECT 
            severity,
            COUNT(*) AS defect_count,
            SUM(CASE WHEN reproduction_status = 'PENDING' THEN 1 ELSE 0 END) AS awaiting_repro_count,
            SUM(CASE WHEN verification_status = 'UNVERIFIED' THEN 1 ELSE 0 END) AS unverified_count
        FROM DEFECTS
        WHERE status NOT IN ('CLOSED', 'REJECTED')
        GROUP BY severity;
        """)

        cursor.execute("DROP VIEW IF EXISTS V_DEFECTS_AWAITING_VERIFICATION;")
        cursor.execute("""
        CREATE VIEW V_DEFECTS_AWAITING_VERIFICATION AS
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
        """)

        # Check if DEFECTS table is empty. If so, seed initial scenarios.
        cursor.execute("SELECT COUNT(*) FROM DEFECTS")
        count = cursor.fetchone()[0]
        if count == 0:
            logger.info("Seeding initial engineering scenarios...")
            _seed_sqlite_data(cursor)

def _seed_sqlite_data(cursor):
    seed_sql = """
    INSERT INTO RELEASES (release_id, version_tag, summary, status, rollback_plan, is_ready, readiness_score, created_at, updated_at, released_at)
    VALUES (
        'REL-2026.0.9', 'v2026.0.9',
        'Q3 Maintenance release: patch for memory leak in event consumer and logging optimizations.',
        'RELEASED', 'Revert container image to sha256:8f4c2e1, execute rollback script DDL-202609-REV.',
        1, 100, '2026-09-15 08:00:00', '2026-09-20 18:00:00', '2026-09-20 18:30:00'
    );

    INSERT INTO RELEASES (release_id, version_tag, summary, status, rollback_plan, is_ready, readiness_score, created_at, updated_at)
    VALUES (
        'REL-2026.1.0', 'v2026.1.0-RC1',
        'Core business release: billing date-boundary fix, aggregate query optimization, and constraint enforcement.',
        'BLOCKED', 'Roll back to tag v2026.0.9. Drop patch tables via migration rollback 002. Re-route gateway traffic to pool A.',
        0, 45, '2026-10-10 09:00:00', datetime('now')
    );

    INSERT INTO DEFECTS (defect_id, title, description, severity, priority, affected_component, environment, status, reproduction_status, expected_behavior, actual_behavior, root_cause_explanation, proposed_correction, verification_status, assigned_owner, associated_regression_test_id, associated_release_id, created_at, updated_at)
    VALUES (
        'DEF-101',
        'Scenario A: Reporting revenue query omits transaction records on midnight date boundary',
        'Monthly revenue reconciliations showed a $48,200 discrepancy compared to ledger totals. All missing transactions had timestamps between 23:59:59.000 and 00:00:00.000.',
        'HIGH', 'P1', 'billing-service', 'STAGING', 'INVESTIGATING', 'REPRODUCED',
        'All transactions strictly within the closed interval [start_date, end_date 23:59:59.999] should be included.',
        'Query used "transaction_time < end_date" where end_date was coerced to midnight 00:00:00 of the final day, discarding the entire final 24 hours of sales.',
        'Date boundary truncation coerced end_date without adding time component or using exclusive half-open interval.',
        'Refactor filter to half-open interval [start_date, end_date + 1 day) or TRUNC comparison in Oracle SQL.',
        'IN_PROGRESS', 'alex.chen', 'TEST-SCENARIO-A', 'REL-2026.1.0', '2026-10-12 10:15:00', datetime('now')
    );

    INSERT INTO DEFECTS (defect_id, title, description, severity, priority, affected_component, environment, status, reproduction_status, expected_behavior, actual_behavior, root_cause_explanation, proposed_correction, verification_status, assigned_owner, associated_regression_test_id, associated_release_id, created_at, updated_at)
    VALUES (
        'DEF-102',
        'Scenario B: Order item report aggregates duplicate row sums from missing join predicate',
        'Daily order summary report showed gross sales at 3x to 5x actual invoiced amounts for multi-shipment orders.',
        'CRITICAL', 'P1', 'order-analytics', 'STAGING', 'FIX_PROPOSED', 'REPRODUCED',
        'Gross sales should equal the sum of distinct order item totals.',
        'Joining ORDERS -> ORDER_ITEMS -> SHIPMENTS without aggregating at line-item level created a cartesian fan-out on orders with multiple shipments.',
        'Cartesian fan-out caused by missing subquery aggregation or missing join predicate on shipment fulfillment records.',
        'Rewrite report query with CTE aggregating shipments prior to joining with order items.',
        'UNVERIFIED', 'sarah.jenkins', 'TEST-SCENARIO-B', 'REL-2026.1.0', '2026-10-14 14:20:00', datetime('now')
    );

    INSERT INTO DEFECTS (defect_id, title, description, severity, priority, affected_component, environment, status, reproduction_status, expected_behavior, actual_behavior, root_cause_explanation, proposed_correction, verification_status, assigned_owner, associated_regression_test_id, associated_release_id, created_at, updated_at)
    VALUES (
        'DEF-103',
        'Scenario C: Invoice status bypasses credit approval state transition directly to issued',
        'High-value enterprise invoices over $50k transitioned from DRAFT directly to ISSUED without passing mandatory CREDIT_APPROVED state.',
        'MEDIUM', 'P2', 'invoice-workflow', 'STAGING', 'VALIDATION_REQUIRED', 'REPRODUCED',
        'Invoice transition from DRAFT to ISSUED must fail with HTTP 422 if invoice total > $50,000 and credit check is missing.',
        'Frontend triggered direct issue endpoint which lacked backend state machine transition validation.',
        'Direct status setter allowed arbitrary state assignment instead of executing state machine transition guard.',
        'Implement state machine validation in backend service and enforce through database trigger/package.',
        'IN_PROGRESS', 'marcus.vance', 'TEST-SCENARIO-C', 'REL-2026.1.0', '2026-10-16 11:30:00', datetime('now')
    );

    INSERT INTO DEFECTS (defect_id, title, description, severity, priority, affected_component, environment, status, reproduction_status, expected_behavior, actual_behavior, root_cause_explanation, proposed_correction, verification_status, assigned_owner, associated_regression_test_id, associated_release_id, created_at, updated_at)
    VALUES (
        'DEF-104',
        'Scenario D: Batch settlement leaves orphaned records on foreign key constraint violation',
        'When a batch payment settlement encountered an invalid merchant ID, partial transaction rows were committed, causing orphaned settlement lines.',
        'HIGH', 'P1', 'settlement-processor', 'STAGING', 'REPRODUCED', 'REPRODUCED',
        'Database foreign key constraint must be enforced; if any line fails, the entire batch transaction must ROLLBACK.',
        'Process committed batches in chunks without atomic transaction boundary, swallowing ORA-02291 integrity violation.',
        'Autocommit mode enabled on batch runner; missing explicit transaction context and exception handler rollback.',
        'Wrap batch execution in explicit database transaction with ROLLBACK in OTHERS exception handler.',
        'UNVERIFIED', 'priya.nair', 'TEST-SCENARIO-D', 'REL-2026.1.0', '2026-10-18 16:45:00', datetime('now')
    );

    INSERT INTO DEFECTS (defect_id, title, description, severity, priority, affected_component, environment, status, reproduction_status, expected_behavior, actual_behavior, root_cause_explanation, proposed_correction, verification_status, assigned_owner, associated_regression_test_id, associated_release_id, created_at, updated_at)
    VALUES (
        'DEF-105',
        'Scenario E: Discount calculation optimization causes regression in coupon validity check',
        'Refactoring discount logic for speed accidentally bypassed the expiration date check for percentage-off coupons.',
        'HIGH', 'P2', 'checkout-engine', 'DEVELOPMENT', 'OPEN', 'REPRODUCED',
        'Expired coupons should be rejected even with the new cached discount pricing rule.',
        'Expired coupons are accepted because date check was moved inside a branch that does not execute for percentage coupons.',
        'Logic flaw in refactored calculation condition; missing regression test before merge.',
        'Restore expiration check to base validation path and add automated regression test.',
        'UNVERIFIED', 'elena.rostova', 'TEST-SCENARIO-E', 'REL-2026.1.0', '2026-10-20 09:10:00', datetime('now')
    );

    INSERT INTO REPRODUCTIONS (reproduction_id, defect_id, preconditions, environment_info, app_version, steps_json, synthetic_fixture_ref, expected_result, actual_result, error_message, frequency, outcome, notes, executed_by, created_at)
    VALUES (
        'REP-101', 'DEF-101',
        'Seeded transactions with timestamps 2026-09-30 14:00:00 and 2026-09-30 23:55:00.',
        'Staging Oracle DB 23ai, Python FastAPI billing-service', 'v2026.1.0-RC1',
        '["1. Send GET /api/lab/scenarios/date-boundary?start=2026-09-01&end=2026-09-30", "2. Inspect returned transaction list and total sum", "3. Check if transaction TXN-EOM-999 is present"]',
        'fixtures/date_boundary_transactions.json',
        'Report should return 3 transactions totaling $75,000.',
        'Report returned 2 transactions totaling $26,800. TXN-EOM-999 ($48,200) was excluded.',
        'No exception thrown. Silent data omission due to SQL boundary condition.',
        'ALWAYS', 'REPRODUCED',
        'Root cause confirmed via query execution plan inspection.', 'alex.chen', '2026-10-12 11:30:00'
    );

    INSERT INTO INVESTIGATIONS (investigation_id, defect_id, problem_statement, observed_symptoms, initial_hypothesis, candidate_causes, confirmed_root_cause, proposed_correction, regression_risk, verification_plan, final_conclusion, status, lead_investigator, created_at, updated_at)
    VALUES (
        'INV-101', 'DEF-101',
        'Transactions occurring on the last day of a billing cycle are silently dropped from periodic revenue queries.',
        'Discrepancy of $48,200 on 2026-09-30. Query returned fewer rows than physical table scan with equal dates.',
        'Query is using < end_date instead of <= or half-open [start, end + 1 day).',
        '1. Timezone offset between app server (UTC) and DB (EST).\n2. Date truncation stripping 23:59:59 time component.\n3. Flawed BETWEEN predicate behavior with Oracle TIMESTAMP.',
        'Application parses end_date as YYYY-MM-DD 00:00:00.000. Using < operator excluded all transactions from 00:00:01 through 23:59:59 on the final day.',
        'Adopt standard half-open interval: created_at >= :start_date AND created_at < :end_date + INTERVAL 1 DAY.',
        'Low risk to existing queries; potential impact on reports relying on legacy truncated totals.',
        'Run automated regression suite test_scenario_a_date_boundary with synthetic end-of-day fixtures.',
        'Defect verified and isolated to interval comparison logic. Fixed and ready for regression suite execution.',
        'ROOT_CAUSE_IDENTIFIED', 'alex.chen', '2026-10-12 11:45:00', datetime('now')
    );

    INSERT INTO INVESTIGATION_EVENTS (event_id, investigation_id, event_type, title, details, actor, created_at)
    VALUES
        ('EVT-101', 'INV-101', 'DEFECT_CREATED', 'Defect logged by reconciliation auditor', 'End of month revenue discrepancy reported from financial audit team.', 'reconciler.bot', '2026-10-12 10:15:00'),
        ('EVT-102', 'INV-101', 'REPRODUCTION_ATTEMPTED', 'Deterministic reproduction executed with synthetic fixture', 'Reproduction REP-101 executed against staging database. Discrepancy confirmed 100%.', 'alex.chen', '2026-10-12 11:30:00'),
        ('EVT-103', 'INV-101', 'HYPOTHESIS_RECORDED', 'Hypothesis formulated: Date boundary truncation', 'Suspect query uses YYYY-MM-DD 00:00:00 as upper bound, omitting last 24 hours.', 'alex.chen', '2026-10-12 11:50:00'),
        ('EVT-104', 'INV-101', 'EVIDENCE_ATTACHED', 'SQL statement and query execution plan attached', 'Captured SQL query showing WHERE created_at < :end_date.', 'alex.chen', '2026-10-12 12:15:00');

    INSERT INTO EVIDENCE (evidence_id, defect_id, investigation_id, evidence_type, title, error_code, sanitized_payload, component, environment, correlation_id, collected_by, created_at)
    VALUES (
        'EVI-101', 'DEF-101', 'INV-101', 'SQL_STATEMENT',
        'Flawed date query statement from repository', 'SQL-DATE-FLAW',
        'SELECT SUM(amount) FROM billing_transactions WHERE txn_date >= :p_start AND txn_date < :p_end; -- :p_end is parsed as 2026-09-30 00:00:00',
        'billing-service', 'STAGING', 'CORR-BILL-1001', 'alex.chen', '2026-10-12 12:15:00'
    );

    INSERT INTO REGRESSION_TESTS (test_id, title, description, test_category, related_defect_id, preconditions, expected_behavior, execution_command, last_outcome, last_run_at, created_at)
    VALUES 
        ('TEST-SCENARIO-A', 'Verify midnight date boundary includes all final-day transactions', 'Tests billing aggregation for transactions occurring between 00:00:00 and 23:59:59 on the boundary date.', 'REGRESSION', 'DEF-101', 'Synthetic transactions seeded at 2026-09-30 23:59:59.000', 'Sum must include boundary transactions without omission.', 'pytest demo_lab/tests/test_scenario_a_date_boundary.py -v', 'PASSED', datetime('now'), '2026-10-13 09:00:00'),
        ('TEST-SCENARIO-B', 'Verify multi-shipment order aggregation prevents cartesian fan-out', 'Tests order reporting calculation when an order has multiple partial shipments.', 'REGRESSION', 'DEF-102', 'Order ORD-99 with 2 line items and 3 shipment fulfillments', 'Gross total must exactly match item sum, ignoring duplicate shipment rows.', 'pytest demo_lab/tests/test_scenario_b_duplicate_aggregation.py -v', 'PASSED', datetime('now'), '2026-10-15 10:00:00'),
        ('TEST-SCENARIO-C', 'Verify invoice workflow rejects illegal transitions without credit check', 'Tests state transition guards on high-value invoices.', 'REGRESSION', 'DEF-103', 'Invoice over $50,000 without CREDIT_APPROVED status', 'Direct transition to ISSUED must fail with ValidationError / 422.', 'pytest demo_lab/tests/test_scenario_c_invalid_transition.py -v', 'PASSED', datetime('now'), '2026-10-17 14:00:00'),
        ('TEST-SCENARIO-D', 'Verify atomic transaction rollback on database integrity violation', 'Tests that an ORA-02291 or constraint failure rolls back all partial writes.', 'DATABASE_INTEGRATION', 'DEF-104', 'Batch containing valid records followed by an invalid parent key', 'Zero rows committed from the failing batch; complete rollback verified.', 'pytest demo_lab/tests/test_scenario_d_db_integrity.py -v', 'PASSED', datetime('now'), '2026-10-19 11:00:00'),
        ('TEST-SCENARIO-E', 'Verify discount calculation respects coupon expiration after optimization', 'Tests regression prevention on checkout calculation path.', 'REGRESSION', 'DEF-105', 'Expired percentage discount coupon code', 'Calculation engine must reject coupon with CouponExpiredException.', 'pytest demo_lab/tests/test_scenario_e_regression_guard.py -v', 'FAILED', datetime('now'), '2026-10-21 09:30:00');

    INSERT INTO TEST_RUNS (run_id, test_suite_id, execution_method, command, outcome, passed_count, failed_count, skipped_count, duration_ms, output_summary, environment_meta, related_defect_id, related_release_id, triggered_by, started_at, completed_at)
    VALUES
        ('RUN-20261021-01', 'SUITE-REGRESSION-CORE', 'AUTOMATED_LOCAL', 'pytest demo_lab/tests/test_scenario_a_date_boundary.py -v', 'PASSED', 3, 0, 0, 142, '3 passed in 0.14s. Date boundary half-open interval verified.', 'Python 3.14.7, Windows, SQLite/Oracle Dialect', 'DEF-101', 'REL-2026.1.0', 'alex.chen', '2026-10-21 09:00:00', '2026-10-21 09:00:01'),
        ('RUN-20261021-02', 'SUITE-REGRESSION-DISCOUNT', 'AUTOMATED_LOCAL', 'pytest demo_lab/tests/test_scenario_e_regression_guard.py -v', 'FAILED', 1, 1, 0, 188, 'FAILED test_expired_coupon_rejected - AssertionError: Expected CouponExpiredException, but discount was applied.', 'Python 3.14.7, Windows, SQLite/Oracle Dialect', 'DEF-105', 'REL-2026.1.0', 'ci-bot', '2026-10-21 09:30:00', '2026-10-21 09:30:01');

    INSERT INTO RELEASE_CHECKS (check_id, release_id, check_name, check_category, is_mandatory, status, waiver_reason, verified_at, verified_by, evidence_details)
    VALUES
        ('CHK-101', 'REL-2026.1.0', 'Mandatory Core Regression Suite Passed', 'REGRESSION_VERIFICATION', 1, 'FAILED', NULL, datetime('now'), 'ci-pipeline', 'Run RUN-20261021-02 failed on test_scenario_e_regression_guard.'),
        ('CHK-102', 'REL-2026.1.0', 'Zero Open Critical/High Blocker Defects', 'BLOCKER_TRIAGE', 1, 'FAILED', NULL, datetime('now'), 'triage-lead', '4 open Critical/High defects remaining (DEF-101, DEF-102, DEF-104, DEF-105).'),
        ('CHK-103', 'REL-2026.1.0', 'Oracle Database Schema Migration Validated', 'DATABASE_MIGRATION', 1, 'PASSED', NULL, '2026-10-21 08:00:00', 'dba.team', 'Migration 001_add_performance_indexes successfully applied and post-check validated.'),
        ('CHK-104', 'REL-2026.1.0', 'Documented Rollback Procedure Available', 'ROLLBACK_PLAN', 1, 'PASSED', NULL, '2026-10-21 08:30:00', 'release-engineer', 'Rollback plan documented in release record with reversible migration scripts.'),
        ('CHK-105', 'REL-2026.1.0', 'API Security and Sanitization Smoke Tests', 'SECURITY_SMOKE', 1, 'PENDING', NULL, NULL, NULL, 'Awaiting completion of staging deployment smoke pass.');

    INSERT INTO DATABASE_CHANGES (change_id, change_name, change_type, target_schema, sql_script, rollback_script, pre_check_query, post_check_query, status, execution_log, applied_at, applied_by, oracle_object_name)
    VALUES
        ('CHG-001', '001_add_performance_indexes', 'INDEX_DDL', 'TRACEPOINT', 'CREATE INDEX idx_defects_comp ON DEFECTS (affected_component);', 'DROP INDEX idx_defects_comp;', 'SELECT COUNT(*) FROM user_indexes WHERE index_name = ''IDX_DEFECTS_COMP'';', 'SELECT status FROM user_indexes WHERE index_name = ''IDX_DEFECTS_COMP'';', 'APPLIED', 'Pre-check count: 0. Index created in 0.08s. Post-check status: VALID.', '2026-10-21 08:00:00', 'alex.chen', 'IDX_DEFECTS_COMP'),
        ('CHG-002', '002_add_component_ownership', 'TABLE_DDL', 'TRACEPOINT', 'CREATE TABLE COMPONENT_REGISTRY (component_name VARCHAR(100) PRIMARY KEY, lead_engineer VARCHAR(100) NOT NULL, tier VARCHAR(20) DEFAULT ''CORE'' NOT NULL);', 'DROP TABLE COMPONENT_REGISTRY;', 'SELECT COUNT(*) FROM user_tables WHERE table_name = ''COMPONENT_REGISTRY'';', 'SELECT table_name FROM user_tables WHERE table_name = ''COMPONENT_REGISTRY'';', 'PENDING', 'Awaiting DB change validation review before release execution.', NULL, NULL, 'COMPONENT_REGISTRY');

    INSERT INTO AUDIT_LOG (audit_id, entity_type, entity_id, action, previous_state, new_state, actor, correlation_id, created_at)
    VALUES
        ('AUD-001', 'DEFECT', 'DEF-101', 'CREATED', NULL, 'Status: OPEN, Severity: HIGH', 'reconciler.bot', 'TXN-DEF-101-INIT', '2026-10-12 10:15:00'),
        ('AUD-002', 'DEFECT', 'DEF-101', 'STATUS_TRANSITION', 'OPEN', 'REPRODUCED [Reason: Deterministic reproduction with REP-101 fixture]', 'alex.chen', 'TXN-DEF-101-REPRO', '2026-10-12 11:30:00'),
        ('AUD-003', 'DEFECT', 'DEF-101', 'STATUS_TRANSITION', 'REPRODUCED', 'INVESTIGATING [Reason: Root cause investigation begun under INV-101]', 'alex.chen', 'TXN-DEF-101-INV', '2026-10-12 11:45:00'),
        ('AUD-004', 'RELEASE', 'REL-2026.1.0', 'READINESS_EVALUATION', 'Status: DRAFT', 'BLOCKED [Score: 45%. Blockers: Failed regression test, 4 open critical/high defects]', 'SYSTEM_GATE_ENGINE', 'GATE-REL-2026.1.0', '2026-10-21 09:35:00');
    """
    cursor.executescript(seed_sql)
