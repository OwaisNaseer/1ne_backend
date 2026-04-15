"""
Tests for YouTube quiz generation endpoint and service helpers.
"""
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.domains.youtube_quiz.routes import youtube_quiz_service
from app.domains.youtube_quiz.schemas import YouTubeQuizGenerateRequest
from app.domains.youtube_quiz.service import YouTubeQuizService


def test_extract_video_id_watch_url():
    video_id = YouTubeQuizService.extract_video_id("https://www.youtube.com/watch?v=sQK3Yr4Sc_k")
    assert video_id == "sQK3Yr4Sc_k"


def test_extract_video_id_short_url():
    video_id = YouTubeQuizService.extract_video_id("https://youtu.be/sQK3Yr4Sc_k")
    assert video_id == "sQK3Yr4Sc_k"


def test_extract_video_id_shorts_url():
    video_id = YouTubeQuizService.extract_video_id("https://www.youtube.com/shorts/sQK3Yr4Sc_k")
    assert video_id == "sQK3Yr4Sc_k"


def test_extract_video_id_invalid_url():
    video_id = YouTubeQuizService.extract_video_id("https://example.com/video/123")
    assert video_id is None


@pytest.mark.asyncio
async def test_generate_endpoint_success(monkeypatch):
    client = TestClient(app, raise_server_exceptions=False)

    async def fake_generate_quiz(_payload):
        return {
            "title": "Sample Video Quiz",
            "summary": "Generated summary",
            "sections": [
                {
                    "heading": "Key idea check",
                    "details": "Core understanding checks",
                    "questions": ["Q1", "Q2"],
                }
            ],
        }

    monkeypatch.setattr(youtube_quiz_service, "generate_quiz", fake_generate_quiz)

    payload = {
        "video_url": "https://www.youtube.com/watch?v=sQK3Yr4Sc_k",
        "grade_band": "Grades 6-8",
        "subject_lens": "Science & STEM",
        "learning_focus": "Concept comprehension",
        "quiz_language": "English",
        "question_styles": ["Multiple choice"],
        "question_count": 6,
    }
    response = client.post("/api/v1/youtube-quiz/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Sample Video Quiz"
    assert isinstance(data["sections"], list)


@pytest.mark.asyncio
async def test_generate_request_invalid_url_validation():
    with pytest.raises(ValidationError):
        YouTubeQuizGenerateRequest(
            video_url="https://example.com/not-youtube",
            grade_band="Grades 6-8",
            subject_lens="Science & STEM",
            learning_focus="Concept comprehension",
            quiz_language="English",
            question_styles=["Multiple choice"],
            question_count=6,
        )


@pytest.mark.asyncio
async def test_generate_endpoint_maps_runtime_error_to_502(monkeypatch):
    client = TestClient(app, raise_server_exceptions=False)
    async def fake_generate_quiz(_payload):
        raise RuntimeError("Provider failure")

    monkeypatch.setattr(youtube_quiz_service, "generate_quiz", fake_generate_quiz)

    payload = {
        "video_url": "https://www.youtube.com/watch?v=sQK3Yr4Sc_k",
        "grade_band": "Grades 6-8",
        "subject_lens": "Science & STEM",
        "learning_focus": "Concept comprehension",
        "quiz_language": "English",
        "question_styles": ["Multiple choice"],
        "question_count": 6,
    }
    response = client.post("/api/v1/youtube-quiz/generate", json=payload)
    assert response.status_code == 502
    assert "Provider failure" in response.json()["detail"]
