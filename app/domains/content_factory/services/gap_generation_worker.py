"""
Background worker utilities for processing gap_detection jobs.

This module is intended to be called from a scheduled task or CLI, not from
the request/response path. It pulls pending jobs and delegates to the
GenerationOrchestratorService, which publishes content into content_registry.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.domains.content_factory.enums import JobStatus
from app.domains.content_factory.models import ContentGenerationJob
from app.domains.content_factory.services.generation_orchestrator_service import (
    GenerationOrchestratorService,
)

logger = get_logger(__name__)


class GapGenerationWorker:
    """Simple async worker loop for gap-detection jobs."""

    def __init__(self, db: Session):
        self.db = db
        self._orchestrator = GenerationOrchestratorService(db)

    def _next_pending_job(self) -> Optional[ContentGenerationJob]:
        return (
            self.db.query(ContentGenerationJob)
            .filter(
                ContentGenerationJob.source == "gap_detection",
                ContentGenerationJob.status == JobStatus.PENDING.value,
            )
            .order_by(ContentGenerationJob.created_at.asc())
            .first()
        )

    async def process_once(self) -> Optional[ContentGenerationJob]:
        """
        Process a single pending gap_detection job, if any.

        Returns the job after orchestration completes or None if no job was found.
        """
        job = self._next_pending_job()
        if not job:
            return None
        logger.info("GapGenerationWorker starting job id=%s topic=%s", job.id, job.topic)
        result = await self._orchestrator.run_micro_course_job(job.id)
        logger.info(
            "GapGenerationWorker completed job id=%s status=%s result_content_id=%s",
            result.id,
            result.status,
            result.result_content_id,
        )
        return result

