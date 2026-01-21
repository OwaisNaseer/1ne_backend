"""
API v1 routes package.
"""
from fastapi import APIRouter

from app.api.v1 import routes_templates, routes_demo
from app.domains.auth import routes as auth_routes
from app.domains.subscriptions import routes as subscription_routes
from app.domains.chatbots import routes as chatbot_routes

router = APIRouter()

# Authentication routes
router.include_router(auth_routes.router)

# Subscription routes
router.include_router(subscription_routes.router)

# Chatbot routes
router.include_router(chatbot_routes.router)

# Core template routes
router.include_router(routes_templates.router)

# Demo routes
router.include_router(routes_demo.router)

