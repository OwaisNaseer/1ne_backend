"""
API v1 routes package.
"""
from fastapi import APIRouter
from app.core.logging import get_logger

logger = get_logger(__name__)

try:
    from app.api.v1 import routes_templates, routes_demo
    from app.domains.auth import routes as auth_routes
    from app.domains.subscriptions import routes as subscription_routes
    from app.domains.chatbots import routes as chatbot_routes
    from app.domains.content_ingestion import routes as content_ingestion_routes
    from app.domains.external_context import routes as metadata_routes
    from app.domains.teacher_identity import routes as teacher_identity_routes
    from app.domains.teacher_intelligence import routes as teacher_intelligence_routes
    from app.domains.learning_hub import routes as learning_hub_routes
    from app.domains.content_registry import routes as content_registry_routes
    from app.domains.content_factory import routes as content_factory_routes
    from app.domains.learning_progress import routes as learning_progress_routes
    from app.domains.recommendation_analytics import routes as recommendation_analytics_routes

    router = APIRouter()
    
    # Authentication routes
    router.include_router(auth_routes.router)
    
    # Metadata (countries, regions, subjects, etc.) and profile context
    router.include_router(metadata_routes.router)

    # Teacher Identity (Professional Learning Hub)
    router.include_router(teacher_identity_routes.router)

    # Teacher Intelligence (CTP, feature snapshots, ML outputs)
    router.include_router(teacher_intelligence_routes.router)

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
    
    # Core template routes
    router.include_router(routes_templates.router)
    
    # Demo routes
    router.include_router(routes_demo.router)
    
    logger.info("All API v1 routes registered successfully")
except Exception as e:
    logger.error(f"Error registering API v1 routes: {e}", exc_info=True)
    raise

