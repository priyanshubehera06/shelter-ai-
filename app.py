"""
app.py — Top-Level FastAPI Application Entrypoint for ShelterAI.
Provides the top-level 'app' instance for Cloud Platforms (Railway, Vercel, Render, Koyeb).
"""

import sys
import os

# Ensure root workspace directory is in Python module search path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Expose top-level FastAPI app instance
from backend.main import app

# Export for ASGI servers (uvicorn app:app / gunicorn app:app)
__all__ = ["app"]

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)