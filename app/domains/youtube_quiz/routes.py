"""
Routes for YouTube quiz generation.
"""
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, status

from app.core.logging import get_logger
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
async def generate_youtube_quiz(payload: YouTubeQuizGenerateRequest) -> YouTubeQuizGenerateResponse:
    """Generate quiz blueprint using YouTube context and LLM output."""
    try:
        return await youtube_quiz_service.generate_quiz(payload)
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
