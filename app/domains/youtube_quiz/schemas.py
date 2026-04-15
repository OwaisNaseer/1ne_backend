"""
Schemas for YouTube quiz generation endpoint.
"""
from typing import List

from pydantic import BaseModel, Field, field_validator


GRADE_BANDS = {
    "Grades 3-5",
    "Grades 6-8",
    "Grades 9-10",
    "Grades 11-12",
    "Higher Education",
}

SUBJECT_LENSES = {
    "Science & STEM",
    "Mathematics",
    "English Language Arts",
    "Social Sciences",
    "Creative Arts & Media",
    "Career & Technical Education",
}

LEARNING_FOCUS_AREAS = {
    "Concept comprehension",
    "Vocabulary development",
    "Critical analysis",
    "Lab skills & procedures",
    "Project reflection",
}

QUIZ_LANGUAGES = {"English", "Spanish", "French", "Arabic", "Hindi"}

QUESTION_STYLES = {
    "Multiple choice",
    "Higher-order thinking",
    "Quick check",
    "Discussion prompt",
}


class YouTubeQuizGenerateRequest(BaseModel):
    """Request payload for quiz generation from a YouTube video."""

    video_url: str = Field(..., min_length=10)
    grade_band: str
    subject_lens: str
    learning_focus: str
    quiz_language: str
    question_styles: List[str] = Field(default_factory=list)
    question_count: int = Field(..., ge=4, le=12)

    @field_validator("video_url")
    @classmethod
    def validate_video_url(cls, value: str) -> str:
        from app.domains.youtube_quiz.service import YouTubeQuizService

        if not YouTubeQuizService.extract_video_id(value):
            raise ValueError("Invalid YouTube URL. Use watch/share/shorts URL formats.")
        return value

    @field_validator("grade_band")
    @classmethod
    def validate_grade_band(cls, value: str) -> str:
        if value not in GRADE_BANDS:
            raise ValueError(f"Unsupported grade_band: {value}")
        return value

    @field_validator("subject_lens")
    @classmethod
    def validate_subject_lens(cls, value: str) -> str:
        if value not in SUBJECT_LENSES:
            raise ValueError(f"Unsupported subject_lens: {value}")
        return value

    @field_validator("learning_focus")
    @classmethod
    def validate_learning_focus(cls, value: str) -> str:
        if value not in LEARNING_FOCUS_AREAS:
            raise ValueError(f"Unsupported learning_focus: {value}")
        return value

    @field_validator("quiz_language")
    @classmethod
    def validate_quiz_language(cls, value: str) -> str:
        if value not in QUIZ_LANGUAGES:
            raise ValueError(f"Unsupported quiz_language: {value}")
        return value

    @field_validator("question_styles")
    @classmethod
    def validate_question_styles(cls, value: List[str]) -> List[str]:
        invalid_styles = [style for style in value if style not in QUESTION_STYLES]
        if invalid_styles:
            raise ValueError(f"Unsupported question styles: {', '.join(invalid_styles)}")
        return value


class YouTubeQuizSection(BaseModel):
    """One quiz output section."""

    heading: str
    details: str
    questions: List[str] = Field(default_factory=list)


class YouTubeQuizGenerateResponse(BaseModel):
    """Response shape expected by frontend quiz preview state."""

    title: str
    summary: str
    sections: List[YouTubeQuizSection]
