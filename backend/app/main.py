"""
FastAPI application entry point.
Configures API, middleware, and lifecycle events.
"""

from contextlib import asynccontextmanager
import logging
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.database import AsyncSessionLocal, close_db, init_db

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.resumes import router as resumes_router
from app.api.v1.endpoints.job_postings import router as job_postings_router

# Configure logging only if not already configured
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME}")
    await init_db()
    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application")
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

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(resumes_router, prefix="/api/v1/resumes", tags=["Resumes"])
app.include_router(
    job_postings_router, prefix="/api/v1/job-postings", tags=["Job Postings"]
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
