"""
Pydantic schemas for Content Factory domain.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ---------- Request ----------
class GenerateMicroCourseRequest(BaseModel):
    """Request to generate a new micro-course."""

    topic: str = Field(..., min_length=1, max_length=255)
    subject: Optional[str] = Field(None, max_length=100)
    grade_band: Optional[str] = Field(None, max_length=50)
    difficulty: Optional[str] = Field(None, max_length=50)
    locale: str = Field(default="en", max_length=20)


# ---------- Job ----------
class ContentGenerationJobResponse(BaseModel):
    """Full job response for detail view."""

    id: UUID
    requested_by_user_id: Optional[UUID] = None
    content_type: str
    generation_strategy: str
    topic: str
    subject: Optional[str] = None
    grade_band: Optional[str] = None
    difficulty: Optional[str] = None
    locale: str
    status: str
    current_step: Optional[str] = None
    retry_count: int = 0
    quality_score: Optional[float] = None
    result_content_id: Optional[str] = None
    error_message: Optional[str] = None
    step_outputs: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContentGenerationJobListItem(BaseModel):
    """Job list item (subset)."""

    id: UUID
    content_type: str
    topic: str
    status: str
    quality_score: Optional[float] = None
    result_content_id: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ---------- Agent output shapes (for validation / typing) ----------
class CurriculumOutput(BaseModel):
    """Output schema from curriculum agent."""

    learning_objectives: List[str] = Field(default_factory=list)
    key_concepts: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    target_skills: List[str] = Field(default_factory=list)


class PedagogyOutput(BaseModel):
    """Output schema from pedagogy agent."""

    instructional_flow: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)
    teaching_strategies: List[str] = Field(default_factory=list)
    teacher_reflections: List[str] = Field(default_factory=list)


class StructureOutput(BaseModel):
    """Output schema from structure agent (micro-course structure)."""

    modules: List[Dict[str, Any]] = Field(default_factory=list)
    lessons: List[Dict[str, Any]] = Field(default_factory=list)
    steps: List[Dict[str, Any]] = Field(default_factory=list)
    activities: List[Dict[str, Any]] = Field(default_factory=list)


class AssessmentOutput(BaseModel):
    """Output schema from assessment agent."""

    practice_tasks: List[Dict[str, Any]] = Field(default_factory=list)
    reflection_prompts: List[str] = Field(default_factory=list)
    mini_quizzes: List[Dict[str, Any]] = Field(default_factory=list)
    rubrics: List[Dict[str, Any]] = Field(default_factory=list)


class ReviewOutput(BaseModel):
    """Output schema from review agent."""

    review_status: str = "pending"
    issues_found: List[str] = Field(default_factory=list)
    improvement_notes: List[str] = Field(default_factory=list)


class QualityOutput(BaseModel):
    """Output schema from quality agent."""

    quality_score: float = 0.0
    quality_feedback: str = ""
    clarity: Optional[float] = None
    pedagogical_depth: Optional[float] = None
    teacher_usefulness: Optional[float] = None
    structure_quality: Optional[float] = None
