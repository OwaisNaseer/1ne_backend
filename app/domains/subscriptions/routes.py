"""
Subscription API routes.
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.logging import get_logger
from app.domains.auth.dependencies import get_current_user, require_role
from app.domains.auth.models import User, RoleName
from app.domains.subscriptions.services.subscription_service import SubscriptionService
from app.domains.subscriptions.services.feature_gate_service import FeatureGateService
from app.domains.subscriptions.services.quota_service import QuotaService
from app.domains.subscriptions.enums import SubscriptionTier
from app.domains.subscriptions.schemas import (
    SubscriptionResponse,
    FeatureAccessResponse,
    UserFeaturesResponse,
    UpgradeTierRequest,
    QuotaSummaryResponse,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/subscriptions", tags=["subscriptions"])


@router.get("/me", response_model=SubscriptionResponse)
def get_my_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user's subscription."""
    service = SubscriptionService(db)
    subscription = service.get_user_subscription(current_user.id)

    return SubscriptionResponse(
        tier=subscription.tier,
        status=subscription.status,
        is_trial=subscription.is_trial,
        is_manually_granted=subscription.is_manually_granted,
        current_period_end=subscription.current_period_end,
        trial_ends_at=subscription.trial_ends_at,
    )


@router.get("/me/features", response_model=UserFeaturesResponse)
def get_my_features(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all features available to current user."""
    service = FeatureGateService(db)
    return service.get_user_features(current_user.id)


@router.get("/me/features/{feature_key}", response_model=FeatureAccessResponse)
def check_feature_access(
    feature_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Check if user has access to a specific feature."""
    service = FeatureGateService(db)
    result = service.check_feature_access(current_user.id, feature_key)

    if not result.has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "feature_not_available",
                "message": result.reason or "Feature not available",
                "upgrade_required": result.upgrade_required,
                "required_tier": result.required_tier,
            },
        )

    return result


@router.get("/me/quota", response_model=QuotaSummaryResponse)
def get_my_quota(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user's quota summary."""
    service = QuotaService(db)
    summary = service.get_quota_summary(current_user.id)
    return QuotaSummaryResponse(**summary)


@router.post("/unlock-premium")
def unlock_premium_for_testing(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Unlock premium for current user (testing only - remove in production)."""
    service = SubscriptionService(db)
    subscription = service.upgrade_user_tier(
        user_id=current_user.id,
        new_tier=SubscriptionTier.PREMIUM,
        granted_by_user_id=current_user.id,
        reason="Self-unlock for testing",
        is_manual=True,
    )

    return {
        "success": True,
        "tier": subscription.tier,
        "message": "Premium unlocked for testing",
    }


@router.post("/admin/upgrade", response_model=SubscriptionResponse)
def upgrade_user_tier(
    request: UpgradeTierRequest,
    current_user: User = Depends(require_role([RoleName.SUPER_ADMIN, RoleName.ORG_ADMIN])),
    db: Session = Depends(get_db),
):
    """Upgrade user tier (admin only - for testing)."""
    service = SubscriptionService(db)

    try:
        new_tier = SubscriptionTier(request.tier)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier: {request.tier}",
        )

    subscription = service.upgrade_user_tier(
        user_id=request.user_id,
        new_tier=new_tier,
        granted_by_user_id=current_user.id,
        reason=request.reason or "Admin upgrade for testing",
        is_manual=True,
    )

    return SubscriptionResponse(
        tier=subscription.tier,
        status=subscription.status,
        is_trial=subscription.is_trial,
        is_manually_granted=subscription.is_manually_granted,
        current_period_end=subscription.current_period_end,
        trial_ends_at=subscription.trial_ends_at,
    )
