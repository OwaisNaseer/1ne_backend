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
    
    router = APIRouter()
    
    # Authentication routes
    router.include_router(auth_routes.router)
    
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

