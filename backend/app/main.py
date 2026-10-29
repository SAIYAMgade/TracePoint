from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time

from .core.config import settings
from .core.logging import logger, generate_correlation_id
from .core.database import init_db, db_manager

from .api.defects_router import router as defects_router
from .api.investigations_router import router as investigations_router
from .api.testing_router import router as testing_router
from .api.releases_router import router as releases_router
from .api.database_changes_router import router as db_changes_router
from .api.reports_router import router as reports_router
from .api.audit_router import router as audit_router
from .api.health_router import router as health_router
from .api.lab_router import router as lab_router

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s in %s mode...", settings.APP_NAME, settings.APP_ENV)
    init_db()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    description="Engineering Intelligence, Root-Cause Analysis, Automated Testing & Release Reliability Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Correlation ID & Request Timing Middleware
@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID") or generate_correlation_id()
    request.state.correlation_id = correlation_id

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    return response

# Centralized Exception Handler for Clean Sanitized Errors
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    correlation_id = getattr(request.state, "correlation_id", "none")
    logger.warning("HTTP %d error on %s: %s [correlation_id: %s]", exc.status_code, request.url.path, exc.detail, correlation_id)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail,
            "correlation_id": correlation_id
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    correlation_id = getattr(request.state, "correlation_id", "none")
    logger.error("Unhandled exception on %s: %s [correlation_id: %s]", request.url.path, str(exc), correlation_id, exc_info=True)
    # Sanitize error to prevent credential or internal path disclosure
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "status_code": 500,
            "message": "Internal system failure. Technical evidence has been recorded.",
            "correlation_id": correlation_id
        }
    )



# Mount API Routers
app.include_router(defects_router, prefix="/api")
app.include_router(investigations_router, prefix="/api")
app.include_router(testing_router, prefix="/api")
app.include_router(releases_router, prefix="/api")
app.include_router(db_changes_router, prefix="/api")
app.include_router(reports_router, prefix="/api")
app.include_router(audit_router, prefix="/api")
app.include_router(health_router, prefix="/api")
app.include_router(lab_router, prefix="/api")

# Mount Static Frontend if built
from fastapi.staticfiles import StaticFiles
frontend_dist = settings.BASE_DIR / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
else:
    @app.get("/")
    def root():
        return {
            "service": settings.APP_NAME,
            "status": "ONLINE",
            "docs": "/api/docs",
            "api_prefix": "/api"
        }
