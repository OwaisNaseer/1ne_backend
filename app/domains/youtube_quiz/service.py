"""
Service layer for generating quizzes from YouTube lessons.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

import requests

from app.core.logging import get_logger
from app.llm.router import ModelRouter
from app.llm.schemas import LLMResponse
from app.domains.youtube_quiz.schemas import (
    YouTubeQuizGenerateRequest,
    YouTubeQuizGenerateResponse,
    QUESTION_STYLES,
)

logger = get_logger(__name__)


class TranscriptUnavailableError(RuntimeError):
    """Raised when transcript cannot be fetched."""


@dataclass
class TranscriptContext:
    video_id: str
    title: str
    transcript_text: str
    used_transcript: bool


class YouTubeQuizService:
    """Build quiz output using transcript context and model router."""

    _model_router: Optional[ModelRouter] = None

    @classmethod
    def _get_model_router(cls) -> ModelRouter:
        if cls._model_router is None:
            cls._model_router = ModelRouter()
        return cls._model_router

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """Extract YouTube video ID from common URL formats."""
        if not url:
            return None
        parsed = urlparse(url.strip())
        host = (parsed.netloc or "").lower()
        path = (parsed.path or "").strip("/")

        if host in {"youtu.be", "www.youtu.be"} and path:
            return path.split("/")[0]

        if "youtube.com" not in host:
            return None

        if path == "watch":
            video_id = parse_qs(parsed.query).get("v", [None])[0]
            return video_id

        if path.startswith("shorts/"):
            parts = path.split("/")
            if len(parts) > 1:
                return parts[1]

        if path.startswith("embed/"):
            parts = path.split("/")
            if len(parts) > 1:
                return parts[1]

        return None

    @staticmethod
    def _extract_json_payload(content: str) -> Dict[str, Any]:
        """Extract JSON object from model content."""
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
            cleaned = re.sub(r"```$", "", cleaned).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start == -1 or end == -1 or end <= start:
                raise
            return json.loads(cleaned[start : end + 1])

    @staticmethod
    def _fetch_video_title(video_url: str) -> Optional[str]:
        """Fetch title via YouTube oEmbed."""
        oembed_url = "https://www.youtube.com/oembed"
        try:
            response = requests.get(
                oembed_url,
                params={"url": video_url, "format": "json"},
                timeout=8,
            )
            if response.status_code != 200:
                return None
            payload = response.json()
            return payload.get("title")
        except Exception:
            return None

    @staticmethod
    def _fetch_transcript(video_id: str, language: str) -> str:
        """Fetch transcript text using youtube-transcript-api if available."""
        try:
            from youtube_transcript_api import YouTubeTranscriptApi

            preferred_languages = [language.lower(), "en"]
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=preferred_languages)
            chunks = [item.get("text", "").strip() for item in transcript if item.get("text")]
            text = " ".join(chunks).strip()
            if not text:
                raise TranscriptUnavailableError("Transcript was empty")
            return text
        except Exception as exc:
            raise TranscriptUnavailableError(str(exc)) from exc

    @staticmethod
    def _truncate_transcript(text: str, max_chars: int = 10000) -> str:
        if len(text) <= max_chars:
            return text
        return text[:max_chars] + " ..."

    @classmethod
    def _build_context(cls, payload: YouTubeQuizGenerateRequest) -> TranscriptContext:
        video_id = cls.extract_video_id(payload.video_url)
        if not video_id:
            raise ValueError("Invalid YouTube URL. Could not extract video id.")

        title = cls._fetch_video_title(payload.video_url) or "YouTube lesson"
        try:
            transcript = cls._fetch_transcript(video_id, payload.quiz_language)
            return TranscriptContext(
                video_id=video_id,
                title=title,
                transcript_text=cls._truncate_transcript(transcript),
                used_transcript=True,
            )
        except TranscriptUnavailableError as exc:
            logger.warning(f"Transcript unavailable for {video_id}: {exc}")
            return TranscriptContext(
                video_id=video_id,
                title=title,
                transcript_text="Transcript unavailable. Rely on video context and educator inputs.",
                used_transcript=False,
            )

    @staticmethod
    def _build_prompt(payload: YouTubeQuizGenerateRequest, context: TranscriptContext) -> tuple[str, str]:
        selected_styles = payload.question_styles or sorted(QUESTION_STYLES)

        system_message = (
            "You are an education assessment assistant. "
            "Always return valid JSON only. "
            "Do not include markdown fences, explanations, or additional keys."
        )
        user_prompt = f"""
Generate a classroom-ready quiz blueprint with this exact schema:
{{
  "title": "string",
  "summary": "string",
  "sections": [
    {{
      "heading": "string",
      "details": "string",
      "questions": ["string", "string"]
    }}
  ]
}}

Rules:
- Keep exactly 3 sections with headings:
  1) Key idea check
  2) Application & transfer
  3) Discussion launcher
- Total questions across all sections should be close to {payload.question_count}.
- Questions must reflect selected styles: {selected_styles}.
- Output language: {payload.quiz_language}
- Grade band: {payload.grade_band}
- Subject lens: {payload.subject_lens}
- Learning focus: {payload.learning_focus}
- If transcript is unavailable, still generate useful pedagogically aligned questions.

Video title: {context.title}
Video id: {context.video_id}
Transcript used: {context.used_transcript}
Transcript/context:
{context.transcript_text}
""".strip()
        return system_message, user_prompt

    @classmethod
    async def _call_model(cls, system_message: str, user_prompt: str) -> LLMResponse:
        router = cls._get_model_router()
        return await router.generate(
            system_message=system_message,
            prompt=user_prompt,
            model_config=None,
        )

    @classmethod
    async def generate_quiz(cls, payload: YouTubeQuizGenerateRequest) -> YouTubeQuizGenerateResponse:
        context = cls._build_context(payload)
        system_message, user_prompt = cls._build_prompt(payload, context)

        try:
            llm_response = await cls._call_model(system_message, user_prompt)
            parsed = cls._extract_json_payload(llm_response.content)
            return YouTubeQuizGenerateResponse.model_validate(parsed)
        except Exception as first_error:
            logger.warning(f"Initial quiz generation parse failed: {first_error}")
            repair_prompt = (
                "Repair the previous response so it is valid JSON for the required schema. "
                "Return JSON only with keys: title, summary, sections[].heading, sections[].details, sections[].questions."
            )
            try:
                llm_response = await cls._call_model(system_message, f"{user_prompt}\n\n{repair_prompt}")
                parsed = cls._extract_json_payload(llm_response.content)
                return YouTubeQuizGenerateResponse.model_validate(parsed)
            except Exception as repair_error:
                logger.error(f"Quiz generation failed after repair attempt: {repair_error}", exc_info=True)
                raise RuntimeError(f"Failed to generate a valid quiz response from LLM. Root error: {str(repair_error)}") from repair_error
