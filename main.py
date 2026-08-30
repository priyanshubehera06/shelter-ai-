"""
main.py — Top-Level FastAPI Application Entrypoint for ShelterAI.
Supports hosting environments running `uvicorn main:app` directly from repo root.
"""

import sys
import os

_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

from backend.main import app

__all__ = ["app"]

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
