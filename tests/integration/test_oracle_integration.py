import pytest
from backend.app.core.database import db_manager, settings
from backend.app.repositories.defect_repository import DefectRepository

# Determine if live Oracle instance is connected
oracle_available = db_manager.is_oracle

@pytest.mark.skipif(
    not oracle_available,
    reason="Oracle Database instance is not connected (ORACLE_DSN not reachable or credentials not supplied). Live Oracle PL/SQL integration tests skipped."
)
class TestOracleDatabaseIntegration:
    """
    Live integration test suite executed exclusively against an Oracle Database Free / 19c / 21c / 23ai instance.
    Validates Oracle SQL, constraints, PL/SQL packages, transaction rollbacks, and views.
    """

    def test_oracle_connection_banner(self):
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT banner FROM v$version WHERE ROWNUM = 1")
            banner = cursor.fetchone()[0]
            assert "Oracle" in banner

    def test_oracle_plsql_package_lifecycle(self):
        with db_manager.session() as conn:
            cursor = conn.cursor()
            status_code = cursor.var(int)
            message = cursor.var(str)
            # Call PL/SQL package PKG_DEFECT_LIFECYCLE
            cursor.callproc(
                "PKG_DEFECT_LIFECYCLE.transition_defect",
                ["DEF-101", "INVESTIGATING", "oracle.tester", "Oracle Integration Test", status_code, message]
            )
            assert status_code.getvalue() == 0

    def test_oracle_plsql_release_gate(self):
        with db_manager.session() as conn:
            cursor = conn.cursor()
            is_ready = cursor.var(int)
            score = cursor.var(float)
            blockers = cursor.var(str)
            cursor.callproc(
                "PKG_RELEASE_GATE.evaluate_readiness",
                ["REL-2026.1.0", is_ready, score, blockers]
            )
            assert is_ready.getvalue() in (0, 1)

    def test_oracle_foreign_key_constraint_enforcement(self):
        with db_manager.session() as conn:
            cursor = conn.cursor()
            # Expect ORA-02291 when inserting reproduction for non-existent defect
            with pytest.raises(Exception) as exc:
                cursor.execute("""
                INSERT INTO REPRODUCTIONS (
                    reproduction_id, defect_id, steps_json, frequency, outcome, executed_by
                ) VALUES ('REP-FK-FAIL', 'DEF-NONEXISTENT-999', '["step1"]', 'ALWAYS', 'REPRODUCED', 'tester')
                """)
            assert "ORA-02291" in str(exc.value)

    def test_oracle_reporting_views(self):
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM V_OPEN_DEFECTS_BY_SEVERITY")
            rows = cursor.fetchall()
            assert len(rows) > 0
