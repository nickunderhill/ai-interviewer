"""
FastAPI application entry point.
Configures API, middleware, and lifecycle events.
"""

from typing import Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import logging
import sys

from app.core.config import settings
from app.core.database import init_db, close_db, AsyncSessionLocal

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

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def root() -> Dict[str, Any]:
    """Root endpoint - basic health check."""
    return {"message": "AI Interviewer API", "status": "running", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
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
            if value == 1:
                db_status = "connected"
            else:
                db_status = "error: unexpected query result"
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status,
        "api": "operational",
    }


@app.get("/api/v1/health", tags=["Health"])
async def health_check_v1() -> Dict[str, str]:
    """
    Health check endpoint for monitoring and deployment verification (v1 API path).
    """
    return {"status": "healthy"}
