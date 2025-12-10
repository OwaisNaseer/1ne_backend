"""
API v1 routes package.
"""
from fastapi import APIRouter

from app.api.v1 import routes_templates, routes_demo

router = APIRouter()

# Core template routes
router.include_router(routes_templates.router)

# Demo routes
router.include_router(routes_demo.router)

