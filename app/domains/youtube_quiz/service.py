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
from pydantic import ValidationError

from app.core.logging import get_logger
from app.domains.youtube_quiz.schemas import QUESTION_STYLE_TO_KEY, QUESTION_STYLES
from app.llm.router import ModelRouter
from app.llm.schemas import LLMResponse
from app.domains.youtube_quiz.schemas import YouTubeQuizGenerateRequest, YouTubeQuizGenerateResponse

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
    _required_section_headings = ["Key idea check", "Application & transfer", "Discussion launcher"]

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
    def _build_style_distribution(selected_styles: List[str], question_count: int) -> Dict[str, int]:
        style_keys = [QUESTION_STYLE_TO_KEY[style] for style in selected_styles]
        if not style_keys:
            return {}

        distribution: Dict[str, int] = {style_key: 0 for style_key in style_keys}
        if len(style_keys) == 1:
            distribution[style_keys[0]] = question_count
            return distribution

        if question_count >= len(style_keys):
            for style_key in style_keys:
                distribution[style_key] = 1
            remaining = question_count - len(style_keys)
        else:
            remaining = question_count

        idx = 0
        while remaining > 0:
            style_key = style_keys[idx % len(style_keys)]
            distribution[style_key] += 1
            remaining -= 1
            idx += 1

        return distribution

    @classmethod
    def _normalize_payload(cls, parsed_payload: Dict[str, Any]) -> Dict[str, Any]:
        sections = parsed_payload.get("sections", [])
        question_counter = 1
        for section_idx, section in enumerate(sections):
            questions = section.get("questions", [])
            for q_idx, question in enumerate(questions):
                if not isinstance(question, dict):
                    continue

                if not question.get("id"):
                    question["id"] = f"q-{section_idx + 1}-{q_idx + 1}-{question_counter}"
                question_counter += 1

                for key in ("prompt", "sample_answer"):
                    value = question.get(key)
                    if isinstance(value, str):
                        question[key] = value.strip()

                options = question.get("options")
                if isinstance(options, list):
                    question["options"] = [str(opt).strip() for opt in options if str(opt).strip()]

                rubric_points = question.get("rubric_points")
                if isinstance(rubric_points, list):
                    question["rubric_points"] = [str(point).strip() for point in rubric_points if str(point).strip()]

        return parsed_payload

    @classmethod
    def _validate_business_rules(
        cls,
        response: YouTubeQuizGenerateResponse,
        expected_style_distribution: Dict[str, int],
        question_count: int,
    ) -> None:
        headings = [section.heading for section in response.sections]
        if headings != cls._required_section_headings:
            raise ValueError(
                f"Sections must be exactly {cls._required_section_headings}. Received headings: {headings}"
            )

        total_questions = sum(len(section.questions) for section in response.sections)
        if total_questions != question_count:
            raise ValueError(
                f"Expected exactly {question_count} questions but received {total_questions}."
            )

        actual_distribution: Dict[str, int] = {}
        for section in response.sections:
            for question in section.questions:
                actual_distribution[question.style] = actual_distribution.get(question.style, 0) + 1

        for style_key, expected_count in expected_style_distribution.items():
            actual_count = actual_distribution.get(style_key, 0)
            if actual_count != expected_count:
                raise ValueError(
                    f"Style distribution mismatch for '{style_key}': expected {expected_count}, got {actual_count}."
                )

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
    def _build_prompt(
        payload: YouTubeQuizGenerateRequest,
        context: TranscriptContext,
        expected_style_distribution: Dict[str, int],
    ) -> tuple[str, str]:
        selected_styles = payload.question_styles or sorted(QUESTION_STYLES)
        selected_style_keys = [QUESTION_STYLE_TO_KEY[style] for style in selected_styles]

        system_message = (
            "You are an education assessment assistant. "
            "Always return valid JSON only. "
            "Do not include markdown fences, explanations, or additional keys."
        )
        schema_string = """
{
  "title": "string",
  "summary": "string",
  "sections": [
    {
      "heading": "Key idea check | Application & transfer | Discussion launcher",
      "details": "string",
      "questions": [
        {
          "id": "string",
          "style": "multiple_choice | higher_order | quick_check | discussion_prompt",
          "prompt": "string",
          "options": ["string", "string", "string", "string"],
          "correct_option_index": 0,
          "sample_answer": "string",
          "rubric_points": ["string", "string"],
          "expected_response_type": "one_word | short_phrase | true_false",
          "answer": "string or boolean"
        }
      ]
    }
  ]
}
""".strip()

        user_prompt = f"""
Generate a classroom-ready quiz blueprint with this exact schema:
{schema_string}

Rules:
- Keep exactly 3 sections with headings:
  1) Key idea check
  2) Application & transfer
  3) Discussion launcher
- Total questions across all sections must be exactly {payload.question_count}.
- Only use these selected styles: {selected_styles} -> mapped keys {selected_style_keys}
- Use this exact style distribution (must match exactly): {expected_style_distribution}
- Output language: {payload.quiz_language}
- Grade band: {payload.grade_band}
- Subject lens: {payload.subject_lens}
- Learning focus: {payload.learning_focus}
- If transcript is unavailable, still generate useful pedagogically aligned questions.
- Question style requirements:
  - multiple_choice: include exactly 4 plausible options and one correct_option_index.
  - higher_order: include sample_answer and at least 2 rubric_points.
  - quick_check: include expected_response_type and exact answer.
  - discussion_prompt: include sample_answer and at least 2 rubric_points with facilitation angles.
- Omit style-specific optional fields for styles where they do not apply.
- Return JSON only. No markdown.

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
    def _validate_and_convert(
        cls,
        parsed_payload: Dict[str, Any],
        expected_style_distribution: Dict[str, int],
        question_count: int,
    ) -> YouTubeQuizGenerateResponse:
        normalized = cls._normalize_payload(parsed_payload)
        response = YouTubeQuizGenerateResponse.model_validate(normalized)
        cls._validate_business_rules(response, expected_style_distribution, question_count)
        return response

    @classmethod
    async def generate_quiz(cls, payload: YouTubeQuizGenerateRequest) -> YouTubeQuizGenerateResponse:
        context = cls._build_context(payload)
        selected_styles = payload.question_styles or sorted(QUESTION_STYLES)
        expected_style_distribution = cls._build_style_distribution(selected_styles, payload.question_count)
        system_message, user_prompt = cls._build_prompt(payload, context, expected_style_distribution)

        llm_response: Optional[LLMResponse] = None
        try:
            llm_response = await cls._call_model(system_message, user_prompt)
            parsed = cls._extract_json_payload(llm_response.content)
            return cls._validate_and_convert(parsed, expected_style_distribution, payload.question_count)
        except Exception as first_error:
            logger.warning(f"Initial quiz generation parse failed: {first_error}")
            previous_response = llm_response.content if llm_response else ""
            validation_errors = (
                first_error.errors() if isinstance(first_error, ValidationError) else [str(first_error)]
            )
            repair_prompt = f"""
Repair the previous response so it is valid JSON for the required schema and business rules.
Return JSON only.

Validation errors:
{validation_errors}

Business rules:
- Required section headings: {cls._required_section_headings}
- Total question count must be exactly {payload.question_count}
- Required style distribution: {expected_style_distribution}
- Style field requirements:
  - multiple_choice: exactly 4 options and valid correct_option_index.
  - higher_order: sample_answer and rubric_points.
  - quick_check: expected_response_type and answer.
  - discussion_prompt: sample_answer and rubric_points.

Original invalid response:
{previous_response}
""".strip()
            try:
                llm_response = await cls._call_model(system_message, f"{user_prompt}\n\n{repair_prompt}")
                parsed = cls._extract_json_payload(llm_response.content)
                return cls._validate_and_convert(parsed, expected_style_distribution, payload.question_count)
            except Exception as repair_error:
                logger.error(f"Quiz generation failed after repair attempt: {repair_error}", exc_info=True)
                raise RuntimeError(
                    "Failed to generate a valid typed quiz response from LLM after repair attempt. "
                    f"Root error: {str(repair_error)}"
                ) from repair_error
