"""
Content Factory API routes.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domains.auth.dependencies import get_current_user, require_any_role
from app.domains.auth.models import User
from app.domains.content_factory import schemas as factory_schemas
from app.domains.content_factory.services import ContentFactoryService

router = APIRouter(prefix="/api/v1/content-factory", tags=["content-factory"])


@router.post(
    "/generate/micro-course",
    response_model=factory_schemas.ContentGenerationJobResponse,
    status_code=status.HTTP_201_CREATED,
)
async def request_micro_course(
    data: factory_schemas.GenerateMicroCourseRequest,
    current_user: User = Depends(require_any_role("super_admin", "org_admin")),
    db: Session = Depends(get_db),
):
    """Request a new micro-course generation (admin). Runs workflow to completion and returns job."""
    service = ContentFactoryService(db)
    job = await service.generate_micro_course(
        topic=data.topic,
        subject=data.subject,
        grade_band=data.grade_band,
        difficulty=data.difficulty,
        locale=data.locale,
        requested_by_user_id=current_user.id,
    )
    return job


@router.get("/jobs", response_model=List[factory_schemas.ContentGenerationJobListItem])
def list_jobs(
    job_status: Optional[str] = Query(None, alias="status"),
    content_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List content generation jobs."""
    service = ContentFactoryService(db)
    jobs = service.list_jobs(
        status=job_status,
        content_type=content_type,
        skip=skip,
        limit=limit,
    )
    return jobs


@router.get("/jobs/{id}", response_model=factory_schemas.ContentGenerationJobResponse)
def get_job(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get job details by id."""
    service = ContentFactoryService(db)
    job = service.get_job(id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job
