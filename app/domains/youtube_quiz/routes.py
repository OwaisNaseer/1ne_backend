"""
Routes for YouTube quiz generation.
"""
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.session import get_db
from app.domains.auth.dependencies import get_current_user
from app.domains.auth.models import User
from app.domains.subscriptions.services.credit_service import CreditService
from app.domains.subscriptions.credit_errors import insufficient_credits_detail
from app.domains.subscriptions.feature_keys import QUIZ_GENERATE
from app.domains.content_factory.constants.lesson_strategies import LESSON_STRATEGIES
from app.domains.youtube_quiz.schemas import (
    YouTubeQuizGenerateRequest,
    YouTubeQuizGenerateResponse,
)
from app.domains.youtube_quiz.service import YouTubeQuizService

logger = get_logger(__name__)

router = APIRouter(tags=["youtube-quiz"])
youtube_quiz_service = YouTubeQuizService()


@router.get(
    "/api/v1/youtube-quiz/lesson-strategies",
    status_code=status.HTTP_200_OK,
)
async def get_lesson_strategies() -> List[Dict[str, Any]]:
    """Return backend-defined lesson strategies for quiz planning."""
    return [
        {
            "id": strategy["id"],
            "title": strategy["title"],
            "teaching_mode": strategy["teaching_mode"],
            "description": strategy["description"],
            "instruction": strategy["instruction"],
            "learning_objectives": strategy["learning_objectives"],
            "base_question_mix": strategy["base_question_mix"],
            "generation_rules": strategy["generation_rules"],
            "recommended_quiz_type": strategy["recommended_quiz_type"],
            "estimated_classroom_time": strategy["estimated_classroom_time"],
            "recommended_export_format": strategy["recommended_export_format"],
            "best_use_case": strategy["best_use_case"],
            "teacher_prompt": strategy["teacher_prompt"],
            "differentiation_note": strategy["differentiation_note"],
        }
        for strategy in LESSON_STRATEGIES.values()
    ]


@router.post(
    "/api/v1/youtube-quiz/generate",
    response_model=YouTubeQuizGenerateResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_youtube_quiz(
    payload: YouTubeQuizGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> YouTubeQuizGenerateResponse:
    """Generate quiz blueprint using YouTube context and LLM output."""
    credit_service = CreditService(db)
    check = credit_service.check_balance(current_user.id)
    cost = credit_service.get_feature_cost(QUIZ_GENERATE)
    if not check.allowed or check.balance < cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=insufficient_credits_detail(
                check,
                cost,
                "You don't have enough credits to generate a quiz.",
            ),
        )
    try:
        result = await youtube_quiz_service.generate_quiz(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.error(f"Unexpected youtube quiz generation error: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected server error while generating quiz.",
        ) from exc
    charge_result = credit_service.charge(
        user_id=current_user.id,
        feature_key=QUIZ_GENERATE,
        llm_response=None,
        description="YouTube quiz generation",
    )
    if charge_result.credits_charged <= 0:
        logger.warning(
            "YouTube quiz generation succeeded but credit charge recorded 0 credits for user %s",
            current_user.id,
        )
    return result
