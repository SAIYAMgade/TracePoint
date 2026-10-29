import subprocess
import time
import re
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import HTTPException
from ..core.config import settings
from ..core.logging import logger
from ..repositories.testing_repository import TestingRepository
from ..repositories.audit_repository import AuditRepository

ALLOWLISTED_COMMANDS = {
    "pytest demo_lab/tests/test_scenario_a_date_boundary.py -v": "TEST-SCENARIO-A",
    "pytest demo_lab/tests/test_scenario_b_duplicate_aggregation.py -v": "TEST-SCENARIO-B",
    "pytest demo_lab/tests/test_scenario_c_invalid_transition.py -v": "TEST-SCENARIO-C",
    "pytest demo_lab/tests/test_scenario_d_db_integrity.py -v": "TEST-SCENARIO-D",
    "pytest demo_lab/tests/test_scenario_e_regression_guard.py -v": "TEST-SCENARIO-E",
    "pytest tests/unit/ -v": "SUITE-UNIT-CORE",
    "pytest tests/api/ -v": "SUITE-API-CORE",
    "pytest demo_lab/tests/ -v": "SUITE-ALL-SCENARIOS"
}

class TestRunnerService:
    @staticmethod
    def execute_test(
        command: str,
        related_defect_id: Optional[str] = None,
        related_release_id: Optional[str] = None,
        triggered_by: str = "developer"
    ) -> Dict[str, Any]:
        # Validate allowlisted command
        norm_cmd = command.strip()
        if norm_cmd not in ALLOWLISTED_COMMANDS:
            raise HTTPException(
                status_code=400,
                detail=f"Security restriction: Execution command '{norm_cmd}' is not in the allowlist. Allowed commands: {list(ALLOWLISTED_COMMANDS.keys())}"
            )

        test_suite_id = ALLOWLISTED_COMMANDS[norm_cmd]
        run_id = f"RUN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"

        start_time = datetime.utcnow()
        t0 = time.time()

        try:
            # Run the command with strict timeout (25 seconds max)
            cmd_parts = ["python", "-m"] + norm_cmd.split()
            result = subprocess.run(
                cmd_parts,
                cwd=str(settings.BASE_DIR),
                capture_output=True,
                text=True,
                timeout=25
            )
            elapsed_ms = int((time.time() - t0) * 1000)
            completed_time = datetime.utcnow()

            stdout = result.stdout or ""
            stderr = result.stderr or ""
            combined_output = stdout + ("\n" + stderr if stderr else "")

            # Parse counts
            passed = 0
            failed = 0
            skipped = 0

            passed_match = re.search(r"(\d+)\s+passed", combined_output)
            if passed_match:
                passed = int(passed_match.group(1))

            failed_match = re.search(r"(\d+)\s+failed", combined_output)
            if failed_match:
                failed = int(failed_match.group(1))

            skipped_match = re.search(r"(\d+)\s+skipped", combined_output)
            if skipped_match:
                skipped = int(skipped_match.group(1))

            outcome = "PASSED" if result.returncode == 0 else "FAILED"

            # Create brief summary
            summary = f"{outcome}: {passed} passed, {failed} failed, {skipped} skipped in {elapsed_ms}ms.\n{combined_output[:1000]}"

        except subprocess.TimeoutExpired:
            elapsed_ms = int((time.time() - t0) * 1000)
            completed_time = datetime.utcnow()
            outcome = "ERROR"
            passed, failed, skipped = 0, 1, 0
            summary = "Execution timed out after 25 seconds."
        except Exception as e:
            elapsed_ms = int((time.time() - t0) * 1000)
            completed_time = datetime.utcnow()
            outcome = "ERROR"
            passed, failed, skipped = 0, 1, 0
            summary = f"Execution error: {str(e)}"

        # Record test run
        run_data = {
            "run_id": run_id,
            "test_suite_id": test_suite_id,
            "execution_method": "AUTOMATED_LOCAL",
            "command": norm_cmd,
            "outcome": outcome,
            "passed_count": passed,
            "failed_count": failed,
            "skipped_count": skipped,
            "duration_ms": elapsed_ms,
            "output_summary": summary,
            "environment_meta": f"Python 3.14, OS: Windows, Dialect: {settings.DB_ENGINE}",
            "related_defect_id": related_defect_id,
            "related_release_id": related_release_id,
            "triggered_by": triggered_by,
            "started_at": start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "completed_at": completed_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        TestingRepository.record_run(run_data)

        # If this command corresponds to a specific test_id in REGRESSION_TESTS, update it
        if test_suite_id.startswith("TEST-"):
            TestingRepository.update_test_outcome(test_suite_id, outcome)

        # Audit
        AuditRepository.record(
            entity_type="TEST_RUN",
            entity_id=run_id,
            action="EXECUTED",
            actor=triggered_by,
            new_state=f"Outcome: {outcome} ({passed} passed, {failed} failed)",
            correlation_id=f"RUN-{run_id}"
        )

        return run_data
