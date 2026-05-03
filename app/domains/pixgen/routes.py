"""
PixGen API routes.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domains.auth.dependencies import get_current_user
from app.domains.auth.models import User
from app.domains.pixgen.schemas import (
    BatchGenerationResponse,
    GenerateBatchRequest,
    GenerateImageRequest,
    GenerationResponse,
    GenerationStatusResponse,
    MyGenerationsResponse,
)
from app.domains.pixgen.services.pixgen_service import PixGenService
from app.domains.subscriptions.services.credit_service import CreditService
from app.domains.subscriptions.credit_errors import insufficient_credits_detail
from app.domains.subscriptions.feature_keys import PIXGEN_IMAGE

router = APIRouter(prefix="/api/v1", tags=["pixgen"])


@router.post("/generate", response_model=GenerationResponse)
@router.post("/pixgen/generate", response_model=GenerationResponse, include_in_schema=False)
def generate_single_image(
    payload: GenerateImageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a single image and store generation metadata."""
    credit_service = CreditService(db)
    check = credit_service.check_balance(current_user.id)
    cost = credit_service.get_feature_cost(PIXGEN_IMAGE)
    if not check.allowed or check.balance < cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=insufficient_credits_detail(
                check,
                cost,
                "You don't have enough credits to generate an image.",
            ),
        )
    service = PixGenService(db)
    try:
        result = service.generate_single(user_id=current_user.id, payload=payload)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Image generation failed: {str(exc)}",
        ) from exc
    if result.imageUrl:
        try:
            credit_service.charge(
                user_id=current_user.id,
                feature_key=PIXGEN_IMAGE,
                llm_response=None,
                description="PixGen image",
            )
        except Exception:
            pass
    return result


@router.post("/generate-batch", response_model=BatchGenerationResponse)
@router.post("/pixgen/generate-batch", response_model=BatchGenerationResponse, include_in_schema=False)
def generate_batch_images(
    payload: GenerateBatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate multiple images for the same prompt parameters."""
    credit_service = CreditService(db)
    check = credit_service.check_balance(current_user.id)
    cost = credit_service.get_feature_cost(PIXGEN_IMAGE)
    total_required = cost * max(1, payload.batchSize)
    if not check.allowed or check.balance < total_required:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=insufficient_credits_detail(
                check,
                total_required,
                "You don't have enough credits for this batch.",
            ),
        )
    service = PixGenService(db)
    try:
        items = service.generate_batch(user_id=current_user.id, payload=payload)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Batch generation failed: {str(exc)}",
        ) from exc
    for item in items:
        if item.imageUrl:
            try:
                credit_service.charge(
                    user_id=current_user.id,
                    feature_key=PIXGEN_IMAGE,
                    llm_response=None,
                    description="PixGen image (batch)",
                )
            except Exception:
                pass
    return BatchGenerationResponse(items=items)


@router.get("/generation-status/{generation_id}", response_model=GenerationStatusResponse)
@router.get("/pixgen/generation-status/{generation_id}", response_model=GenerationStatusResponse, include_in_schema=False)
def get_generation_status(
    generation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get generation status (sync today, polling-friendly for future async)."""
    service = PixGenService(db)
    status_item = service.get_generation_status(user_id=current_user.id, generation_id=generation_id)
    if not status_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generation not found")
    return status_item


@router.get("/my-generations", response_model=MyGenerationsResponse)
@router.get("/pixgen/my-generations", response_model=MyGenerationsResponse, include_in_schema=False)
def my_generations(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List generation history for the current user."""
    service = PixGenService(db)
    items = service.list_user_generations(user_id=current_user.id, limit=limit, offset=offset)
    return MyGenerationsResponse(items=items)
