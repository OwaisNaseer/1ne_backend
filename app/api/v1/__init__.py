"""
API v1 routes package.

Only registers routers whose `routes` modules exist in this checkout.
(Incomplete domain trees would otherwise break the entire app import.)
"""
from fastapi import APIRouter

from app.core.logging import get_logger

logger = get_logger(__name__)

<<<<<<< HEAD
from app.api.v1 import routes_templates, routes_demo
from app.domains.auth import routes as auth_routes
from app.domains.subscriptions import routes as subscription_routes
from app.domains.chatbots import routes as chatbot_routes
from app.domains.pixgen import routes as pixgen_routes
from app.domains.youtube_quiz import routes as youtube_quiz_routes
=======
try:
    from app.api.v1 import routes_templates, routes_demo
    from app.domains.auth import routes as auth_routes
    from app.domains.subscriptions import routes as subscription_routes
    from app.domains.chatbots import routes as chatbot_routes
    from app.domains.content_ingestion import routes as content_ingestion_routes
    from app.domains.content_ingestion.quiz_catalog_routes import router as quiz_catalog_router
    from app.domains.external_context import routes as metadata_routes
    from app.domains.teacher_identity import routes as teacher_identity_routes
    from app.domains.teacher_intelligence import routes as teacher_intelligence_routes
    from app.domains.learning_hub import routes as learning_hub_routes
    from app.domains.content_registry import routes as content_registry_routes
    from app.domains.content_factory import routes as content_factory_routes
    from app.domains.learning_progress import routes as learning_progress_routes
    from app.domains.recommendation_analytics import routes as recommendation_analytics_routes
    from app.domains.personalization import routes as personalization_routes
>>>>>>> 1bbfddc0c16cafbd69938c796c15e577f3701719

router = APIRouter()

router.include_router(auth_routes.router)
router.include_router(subscription_routes.router)
router.include_router(chatbot_routes.router)
router.include_router(pixgen_routes.router)

router.include_router(routes_templates.router)
router.include_router(routes_demo.router)

<<<<<<< HEAD
router.include_router(youtube_quiz_routes.router)
=======
    # Learning Hub (Pipeline2 integration, home orchestration)
    router.include_router(learning_hub_routes.router)

    # Content Registry (canonical content + recommendation mapping)
    router.include_router(content_registry_routes.router)

    # Content Factory (agentic content generation)
    router.include_router(content_factory_routes.router)

    # Learning Progress (sessions, events, feedback)
    router.include_router(learning_progress_routes.router)

    # Recommendation Analytics (performance snapshots)
    router.include_router(recommendation_analytics_routes.router)

    # Personalization (persistent user personalization profile + unlock + activity)
    router.include_router(personalization_routes.router)
    router.include_router(personalization_routes.admin_router)
    router.include_router(personalization_routes.activity_router)
    router.include_router(personalization_routes.content_router)

    # Subscription routes
    router.include_router(subscription_routes.router)
    
    # Chatbot routes
    router.include_router(chatbot_routes.router)
    
    # Content Ingestion routes
    try:
        router.include_router(content_ingestion_routes.router)
        logger.info("Content ingestion routes registered successfully")
    except Exception as e:
        logger.error(f"Failed to register content ingestion routes: {e}", exc_info=True)
        raise

    # Quiz Catalog routes
    router.include_router(quiz_catalog_router)
    
    # Core template routes
    router.include_router(routes_templates.router)
    
    # Demo routes
    router.include_router(routes_demo.router)
    
    logger.info("All API v1 routes registered successfully")
except Exception as e:
    logger.error(f"Error registering API v1 routes: {e}", exc_info=True)
    raise
>>>>>>> 1bbfddc0c16cafbd69938c796c15e577f3701719

logger.info("API v1 routes registered (auth, subscriptions, chatbots, pixgen, templates, demo, youtube-quiz)")
