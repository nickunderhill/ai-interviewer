"""
FastAPI application entry point.
Configures API, middleware, and lifecycle events.
"""

from contextlib import asynccontextmanager
import logging
import os
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.job_postings import router as job_postings_router
from app.api.v1.endpoints.metrics import router as metrics_router
from app.api.v1.endpoints.operations import router as operations_router
from app.api.v1.endpoints.resumes import router as resumes_router
from app.api.v1.endpoints.sessions import router as sessions_router
from app.api.v1.endpoints.users import router as users_router
from app.core.config import settings
from app.core.database import AsyncSessionLocal, close_db, init_db
from app.core.logging_config import configure_logging
from app.middleware.security_headers import SecurityHeadersMiddleware

# Configure structured JSON logging (idempotent)
configure_logging(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME}")
    skip_db_init = (
        os.getenv("PYTEST_CURRENT_TEST") is not None
        or os.getenv("DISABLE_STARTUP_DB_CHECK") == "1"
    )
    if skip_db_init:
        logger.info("Skipping DB init during tests")
    else:
        await init_db()
    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application")
    if skip_db_init:
        logger.info("Skipping DB close during tests")
    else:
        await close_db()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered mock interview system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


@app.exception_handler(OperationalError)
async def db_connection_exception_handler(request: Request, exc: OperationalError):
    """
    Handle database connection errors globally.
    Returns 503 Service Unavailable instead of 500 Internal Server Error.
    """
    logger.error(f"Database connection error: {str(exc)}")
    return JSONResponse(
        status_code=503,
        content={
            "code": "SERVICE_UNAVAILABLE",
            "message": "The service is temporarily unavailable due to a database connection issue. Please try again later.",
        },
    )


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(resumes_router, prefix="/api/v1/resumes", tags=["Resumes"])
app.include_router(
    job_postings_router, prefix="/api/v1/job-postings", tags=["Job Postings"]
)
app.include_router(sessions_router, prefix="/api/v1/sessions", tags=["Sessions"])
app.include_router(operations_router, prefix="/api/v1/operations", tags=["Operations"])
app.include_router(metrics_router, prefix="/api/v1/metrics", tags=["Metrics"])

# Add Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/", tags=["Health"])
async def root() -> dict[str, Any]:
    """Root endpoint - basic health check."""
    return {"message": "AI Interviewer API", "status": "running", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint.
    Verifies database connectivity and application status.
    """
    try:
        # Test database connection
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            value = result.scalar()
            # Validate query actually returned expected result
            db_status = "connected" if value == 1 else "error: unexpected query result"
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status,
        "api": "operational",
    }


@app.get("/api/v1/health", tags=["Health"])
async def health_check_v1() -> dict[str, str]:
    """
    Health check endpoint for monitoring and deployment verification (v1 API path).
    """
    return {"status": "healthy"}
