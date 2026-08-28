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

# Configure CORS for React / Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes under both /api and / for compatibility with serverless reverse proxies
app.include_router(api_router, prefix=settings.API_PREFIX)
app.include_router(api_router)


@app.get("/api/health", tags=["System"])
@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint to verify API and Engine readiness."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
