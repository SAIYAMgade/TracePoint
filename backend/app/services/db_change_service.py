from typing import Dict, Any
from datetime import datetime
from fastapi import HTTPException
from ..repositories.db_change_repository import DBChangeRepository
from ..repositories.audit_repository import AuditRepository
from ..core.database import db_manager
from ..core.logging import logger

class DBChangeService:
    @staticmethod
    def execute_validation_migration(change_id: str, applied_by: str = "dba.engineer") -> Dict[str, Any]:
        change = DBChangeRepository.get_by_id(change_id)
        if not change:
            raise HTTPException(status_code=404, detail=f"Database change {change_id} not found")

        log_lines = []
        pre_ok = True
        applied_ok = False
        post_ok = False

        log_lines.append(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] Starting controlled migration: {change['change_name']}")

        with db_manager.session() as conn:
            cursor = conn.cursor()

            # 1. Pre-check
            if change.get("pre_check_query"):
                try:
                    cursor.execute(change["pre_check_query"])
                    res = cursor.fetchone()
                    log_lines.append(f"Pre-check executed. Result: {res[0] if res else 'None'}")
                except Exception as e:
                    pre_ok = False
                    log_lines.append(f"Pre-check error: {str(e)}")

            # 2. Up migration execution
            try:
                # In SQLite or Oracle, execute the DDL
                cursor.execute(change["sql_script"])
                applied_ok = True
                log_lines.append("Up migration SQL executed successfully.")
            except Exception as e:
                applied_ok = False
                log_lines.append(f"Up migration failed: {str(e)}")

            # 3. Post-check
            if applied_ok and change.get("post_check_query"):
                try:
                    cursor.execute(change["post_check_query"])
                    res = cursor.fetchone()
                    post_ok = True
                    log_lines.append(f"Post-check verified. Result: {res[0] if res else 'None'}")
                except Exception as e:
                    post_ok = False
                    log_lines.append(f"Post-check verification failed: {str(e)}")
            elif applied_ok:
                post_ok = True

            final_status = "APPLIED" if (applied_ok and post_ok) else "FAILED"
            full_log = "\n".join(log_lines)

            DBChangeRepository.update_status(change_id, final_status, full_log, applied_by)

            AuditRepository.record(
                entity_type="DATABASE_CHANGE",
                entity_id=change_id,
                action="MIGRATION_EXECUTED",
                actor=applied_by,
                new_state=f"Status: {final_status}",
                correlation_id=f"MIG-{change_id}"
            )

            return {
                "change_id": change_id,
                "pre_check_passed": pre_ok,
                "applied_successfully": applied_ok,
                "post_check_passed": post_ok,
                "execution_log": full_log,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            }
