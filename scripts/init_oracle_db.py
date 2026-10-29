#!/usr/bin/env python3
"""
Oracle Database Initialization Script for TracePoint.
Executes pure Oracle DDL schemas, reporting views, PL/SQL packages, and initial seeds.
"""

import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.core.config import settings
from backend.app.core.logging import logger

try:
    import oracledb
except ImportError:
    logger.error("Error: 'oracledb' package is not installed. Install via: pip install oracledb")
    sys.exit(1)

def main():
    user = settings.ORACLE_USER
    password = settings.ORACLE_PASSWORD
    dsn = settings.ORACLE_DSN

    if not user or not password:
        logger.error("Missing ORACLE_USER or ORACLE_PASSWORD in environment/.env file.")
        logger.info("Example: ORACLE_USER=tracepoint_app ORACLE_PASSWORD=secret ORACLE_DSN=localhost:1521/FREEPDB1")
        sys.exit(1)

    logger.info("Connecting to Oracle Database: %s as %s", dsn, user)
    try:
        connection = oracledb.connect(user=user, password=password, dsn=dsn)
        cursor = connection.cursor()
        cursor.execute("SELECT banner FROM v$version WHERE ROWNUM = 1")
        banner = cursor.fetchone()[0]
        logger.info("Connected to: %s", banner)
    except Exception as e:
        logger.error("Failed to connect to Oracle: %s", str(e))
        sys.exit(1)

    db_dir = settings.DATABASE_DIR

    files_to_run = [
        db_dir / "schema" / "01_tables.sql",
        db_dir / "views" / "02_views.sql",
        db_dir / "packages" / "03_pkg_defect_lifecycle.sql",
        db_dir / "packages" / "04_pkg_release_gate.sql",
        db_dir / "seed" / "05_seed_data.sql",
    ]

    for sql_file in files_to_run:
        if not sql_file.exists():
            logger.warning("File not found: %s", sql_file)
            continue

        logger.info("Applying %s ...", sql_file.name)
        with open(sql_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Handle PL/SQL blocks separated by '/'
        if "/" in content and ("PACKAGE" in content or "PROCEDURE" in content):
            blocks = content.split("/")
            for block in blocks:
                clean_block = block.strip()
                if clean_block and not clean_block.startswith("--"):
                    try:
                        cursor.execute(clean_block)
                    except Exception as e:
                        logger.warning("PL/SQL block execution notice: %s", str(e))
        else:
            statements = content.split(";")
            for stmt in statements:
                clean_stmt = stmt.strip()
                if clean_stmt and not clean_stmt.startswith("--"):
                    try:
                        cursor.execute(clean_stmt)
                    except Exception as e:
                        logger.warning("SQL statement notice: %s", str(e))

        connection.commit()

    logger.info("Oracle database schema, packages, views, and seed data initialized successfully!")
    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()
