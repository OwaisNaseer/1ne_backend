"""
Content Factory domain models.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Float,
    DateTime,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.db.base import Base


class ContentGenerationJob(Base):
    """Tracks an agentic content generation run from request to publish."""

    __tablename__ = "content_generation_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    requested_by_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    content_type = Column(String(50), nullable=False, index=True)
    generation_strategy = Column(String(50), nullable=False)
    topic = Column(String(255), nullable=False)
    subject = Column(String(100), nullable=True)
    grade_band = Column(String(50), nullable=True)
    difficulty = Column(String(50), nullable=True)
    locale = Column(String(20), default="en", nullable=False)

    status = Column(String(50), nullable=False, index=True)
    current_step = Column(String(50), nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    quality_score = Column(Float, nullable=True)
    result_content_id = Column(String(150), nullable=True)
    error_message = Column(Text, nullable=True)

    # Intermediate outputs per step (curriculum, pedagogy, structure, assessment, review, quality)
    step_outputs = Column(JSONB, default=dict, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<ContentGenerationJob(id={self.id}, status={self.status}, "
            f"content_type={self.content_type}, topic={self.topic})>"
        )
