from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.db.session import init_db
from app.api.v1.api import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup sequence
    setup_logging()
    logger.info("Initializing CareIntel AI Backend...")
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database on startup: {e}", exc_info=True)
    yield
    # Shutdown sequence
    logger.info("CareIntel AI Backend shutting down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "CareIntel AI is a healthcare lead intelligence platform designed to transform "
        "publicly available healthcare business information into structured, actionable lead data."
    ),
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware for React Vite frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register v1 API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Ensures backend errors are logged internally with stack traces
    while shielding frontend clients from raw tracebacks.
    """
    logger.error(f"Unhandled exception processing {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred while processing the request. Technical details have been logged.",
            "path": str(request.url.path)
        }
    )

@app.get("/", tags=["Root"])
def root():
    return {
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "phase": "Phase 1 - Lead Discovery & Data Intelligence",
        "documentation": "/docs",
        "health_check": f"{settings.API_V1_STR}/health"
    }

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
