import os
from typing import Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Interviewer API",
    description="Backend API for AI-powered technical interview practice system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for frontend integration
# Allow origins from environment variable, default to localhost for development
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def root() -> Dict[str, Any]:
    """
    Root endpoint - health check.
    Returns basic API information and status.
    """
    return {
        "message": "AI Interviewer API",
        "status": "operational",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/api/v1/health", tags=["Health"])
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for monitoring and deployment verification.
    """
    return {"status": "healthy"}
