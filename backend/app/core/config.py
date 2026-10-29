import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "TracePoint")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    API_HOST: str = os.getenv("API_HOST", "127.0.0.1")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    DB_ENGINE: str = os.getenv("DB_ENGINE", "sqlite").lower()
    ORACLE_USER: str = os.getenv("ORACLE_USER", "")
    ORACLE_PASSWORD: str = os.getenv("ORACLE_PASSWORD", "")
    ORACLE_DSN: str = os.getenv("ORACLE_DSN", "localhost:1521/FREEPDB1")
    ORACLE_WALLET_DIR: str = os.getenv("ORACLE_WALLET_DIR", "")
    ORACLE_CONFIG_DIR: str = os.getenv("ORACLE_CONFIG_DIR", "")

    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "tracepoint.db")
    
    # Absolute paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    DATABASE_DIR: Path = BASE_DIR / "database"

settings = Settings()
