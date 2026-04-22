"""
API v1 routes package.

Registers routers that exist in this checkout. Optional domains are wrapped so a
missing or broken submodule does not prevent core APIs (auth, templates, PixGen,
YouTube quiz, content ingestion) from loading.
"""
from fastapi import APIRouter

from app.core.logging import get_logger

logger = get_logger(__name__)

from app.api.v1 import routes_templates, routes_demo
from app.domains.auth import routes as auth_routes
from app.domains.chatbots import routes as chatbot_routes
from app.domains.pixgen import routes as pixgen_routes
from app.domains.subscriptions import routes as subscription_routes
from app.domains.youtube_quiz import routes as youtube_quiz_routes

router = APIRouter()

router.include_router(auth_routes.router)
router.include_router(subscription_routes.router)
router.include_router(chatbot_routes.router)
router.include_router(pixgen_routes.router)
router.include_router(routes_templates.router)
router.include_router(routes_demo.router)
router.include_router(youtube_quiz_routes.router)

try:
    from app.domains.content_ingestion import routes as content_ingestion_routes
    from app.domains.content_ingestion.quiz_catalog_routes import router as quiz_catalog_router

    router.include_router(content_ingestion_routes.router)
    router.include_router(quiz_catalog_router)
    logger.info("Content ingestion and quiz catalog routes registered")
except Exception as exc:
    logger.warning(
        "Content ingestion / quiz catalog routes not registered (incomplete checkout or import error): %s",
        exc,
    )

try:
    from app.domains.learning_hub import routes as learning_hub_routes

    router.include_router(learning_hub_routes.router)
    logger.info("Learning Hub routes registered")
except Exception as exc:
    logger.warning("Learning Hub routes not registered: %s", exc)

_optional_domains = [
    ("content_registry", "app.domains.content_registry.routes", "router"),
    ("content_factory", "app.domains.content_factory.routes", "router"),
    ("learning_progress", "app.domains.learning_progress.routes", "router"),
    ("recommendation_analytics", "app.domains.recommendation_analytics.routes", "router"),
    ("external_context", "app.domains.external_context.routes", "router"),
    ("teacher_identity", "app.domains.teacher_identity.routes", "router"),
    ("teacher_intelligence", "app.domains.teacher_intelligence.routes", "router"),
]

for label, module_path, attr in _optional_domains:
    try:
        mod = __import__(module_path, fromlist=[attr])
        sub = getattr(mod, attr, None)
        if sub is not None:
            router.include_router(sub)
            logger.info("%s routes registered", label)
    except Exception as exc:
        logger.warning("%s routes skipped: %s", label, exc)

try:
    from app.domains.personalization import routes as personalization_routes

    router.include_router(personalization_routes.router)
    router.include_router(personalization_routes.admin_router)
    router.include_router(personalization_routes.activity_router)
    router.include_router(personalization_routes.content_router)
    logger.info("Personalization routes registered")
except Exception as exc:
    logger.warning("Personalization routes not registered: %s", exc)

logger.info(
    "API v1 routes registered (core + optional domains where available)"
)
