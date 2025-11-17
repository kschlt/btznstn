"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Betzenstein Booking API",
    description="Booking & Approval system for Betzenstein",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration - will be configured via environment variables in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "message": "Betzenstein Booking API"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Detailed health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}
