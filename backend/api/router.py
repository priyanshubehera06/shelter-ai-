"""
router.py — Primary API Router aggregating all REST endpoints for ShelterAI.
"""

from fastapi import APIRouter
from backend.api.routes import (
    climate,
    materials,
    designs,
    simulation,
    optimization,
    digital_twin,
    results,
)

api_router = APIRouter()

api_router.include_router(climate.router)
api_router.include_router(materials.router)
api_router.include_router(designs.router)
api_router.include_router(simulation.router)
api_router.include_router(optimization.router)
api_router.include_router(digital_twin.router)
api_router.include_router(results.router)
