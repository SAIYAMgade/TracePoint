#!/usr/bin/env python3
"""
Launcher script for TracePoint Backend API.
Starts uvicorn server on configured host and port.
"""

import sys
import uvicorn
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.core.config import settings

def main():
    print(f"Starting {settings.APP_NAME} on http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"API Docs available at: http://{settings.API_HOST}:{settings.API_PORT}/api/docs")
    print(f"Active Database Dialect: {settings.DB_ENGINE.upper()}")
    uvicorn.run(
        "backend.app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=False
    )

if __name__ == "__main__":
    main()
