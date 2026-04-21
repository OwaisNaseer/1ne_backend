"""
API v1 routes package.

Only registers routers whose `routes` modules exist in this checkout.
(Incomplete domain trees would otherwise break the entire app import.)
"""
from fastapi import APIRouter

from app.core.logging import get_logger

logger = get_logger(__name__)

from app.api.v1 import routes_templates, routes_demo
from app.domains.auth import routes as auth_routes
from app.domains.subscriptions import routes as subscription_routes
from app.domains.chatbots import routes as chatbot_routes
from app.domains.pixgen import routes as pixgen_routes
from app.domains.youtube_quiz import routes as youtube_quiz_routes

router = APIRouter()

router.include_router(auth_routes.router)
router.include_router(subscription_routes.router)
router.include_router(chatbot_routes.router)
router.include_router(pixgen_routes.router)

router.include_router(routes_templates.router)
router.include_router(routes_demo.router)

router.include_router(youtube_quiz_routes.router)

logger.info("API v1 routes registered (auth, subscriptions, chatbots, pixgen, templates, demo, youtube-quiz)")
