"""
Routes for YouTube quiz generation.
"""
from fastapi import APIRouter, HTTPException, status

from app.core.logging import get_logger
from app.domains.youtube_quiz.schemas import (
    YouTubeQuizGenerateRequest,
    YouTubeQuizGenerateResponse,
)
from app.domains.youtube_quiz.service import YouTubeQuizService

logger = get_logger(__name__)

router = APIRouter(tags=["youtube-quiz"])
youtube_quiz_service = YouTubeQuizService()


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
