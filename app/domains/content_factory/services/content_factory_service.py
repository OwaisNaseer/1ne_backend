"""
Content Factory Service: main entry for generating micro-courses.
Creates job and runs orchestrator.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.domains.content_factory.enums import ContentGenerationStrategy, JobStatus
from app.domains.content_factory.models import ContentGenerationJob
from app.domains.content_factory.services.generation_orchestrator_service import (
    GenerationOrchestratorService,
)

logger = get_logger(__name__)


class ContentFactoryServiceError(Exception):
    """Raised when content factory operation fails."""
    pass


class ContentFactoryService:
    """Main service: create generation job and run micro-course workflow."""

    def __init__(self, db: Session):
        self.db = db

    def create_job(
        self,
        content_type: str,
        topic: str,
        subject: Optional[str] = None,
        grade_band: Optional[str] = None,
        difficulty: Optional[str] = None,
        locale: str = "en",
        requested_by_user_id: Optional[UUID] = None,
        generation_strategy: str = ContentGenerationStrategy.TOPIC_BASED.value,
    ) -> ContentGenerationJob:
        """Create a pending content generation job."""
        job = ContentGenerationJob(
            requested_by_user_id=requested_by_user_id,
            content_type=content_type,
            generation_strategy=generation_strategy,
            topic=topic,
            subject=subject,
            grade_band=grade_band,
            difficulty=difficulty,
            locale=locale,
            status=JobStatus.PENDING.value,
            current_step=None,
            retry_count=0,
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        logger.info("Created content generation job id=%s topic=%s", job.id, topic)
        return job

    def get_job(self, job_id: UUID) -> Optional[ContentGenerationJob]:
        """Get job by id."""
        return self.db.query(ContentGenerationJob).filter(ContentGenerationJob.id == job_id).first()

    def list_jobs(
        self,
        status: Optional[str] = None,
        content_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[ContentGenerationJob]:
        """List jobs with optional filters."""
        q = self.db.query(ContentGenerationJob).order_by(ContentGenerationJob.created_at.desc())
        if status is not None:
            q = q.filter(ContentGenerationJob.status == status)
        if content_type is not None:
            q = q.filter(ContentGenerationJob.content_type == content_type)
        return q.offset(skip).limit(limit).all()

    async def generate_micro_course(
        self,
        topic: str,
        subject: Optional[str] = None,
        grade_band: Optional[str] = None,
        difficulty: Optional[str] = None,
        locale: str = "en",
        requested_by_user_id: Optional[UUID] = None,
    ) -> ContentGenerationJob:
        """
        Create a micro-course generation job and run the workflow synchronously (blocking).
        Returns the job after completion or failure.
        """
        job = self.create_job(
            content_type="micro_course",
            topic=topic,
            subject=subject,
            grade_band=grade_band,
            difficulty=difficulty,
            locale=locale,
            requested_by_user_id=requested_by_user_id,
            generation_strategy=ContentGenerationStrategy.TOPIC_BASED.value,
        )
        orchestrator = GenerationOrchestratorService(self.db)
        return await orchestrator.run_micro_course_job(job.id)
