"""
main.py — FastAPI Application Entrypoint for ShelterAI Full-Stack Platform.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.core.config import settings
from backend.core.logging import logger
from backend.api.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Software Based Model Development for Design of Area Specific Shelter for Thermal Comfort Maintenance.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for React / Vite frontend and Vercel preview environments
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"^https:\/\/.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint for health and discovery
@app.get("/", tags=["System"])
def root():
    """Root status endpoint."""
    return {
        "name": "ShelterAI API",
        "status": "running"
    }


# Health check endpoint for Render / Load Balancers
@app.get("/health", tags=["System"])
def health():
    """Ultra-fast health check endpoint for deployment monitoring."""
    return {
        "status": "ok"
    }


@app.get("/api/health", tags=["System"])
def api_health():
    """API health check endpoint returning system status and metadata."""
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }


# Register API routes under both /api and / for compatibility with reverse proxies
app.include_router(api_router, prefix=settings.API_PREFIX)
app.include_router(api_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler preventing stack trace leaks in production."""
    logger.error(f"Global exception on {request.url.path}: {str(exc)}", exc_info=True)
    error_msg = "The thermal simulation or server operation could not be completed."
    detail_msg = error_msg if settings.ENVIRONMENT == "production" else f"Internal Server Error: {str(exc)}"
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": error_msg
            },
            "detail": detail_msg
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=(settings.ENVIRONMENT == "development"))
