"""
Learning Hub API routes: Pipeline2 run, home, home/refresh.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domains.auth.dependencies import get_current_user
from app.domains.auth.models import User
from app.domains.learning_hub import schemas as hub_schemas
from app.domains.learning_hub.services import (
    Pipeline2IntegrationService,
    LearningHubHomeService,
)
from app.domains.teacher_intelligence import schemas as ti_schemas

router = APIRouter(prefix="/api/v1/learning-hub", tags=["learning-hub"])


@router.post(
    "/pipeline2/run",
    response_model=ti_schemas.MLOutputResponse,
    status_code=status.HTTP_201_CREATED,
)
def run_pipeline2(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Run Pipeline2 for the current user. Requires a feature snapshot."""
    service = Pipeline2IntegrationService(db)
    try:
        output = service.run_pipeline2_for_teacher(current_user.id)
        return output
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Pipeline2 run failed: {e!s}",
        )


@router.get("/home", response_model=hub_schemas.LearningHubHomeResponse)
def get_home(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get Learning Hub home payload for the current user."""
    service = LearningHubHomeService(db)
    return service.get_home(current_user.id)


@router.post("/home/refresh", response_model=hub_schemas.LearningHubHomeResponse)
def refresh_home(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Rebuild and return Learning Hub home payload (V1: no persistence of snapshot)."""
    service = LearningHubHomeService(db)
    return service.get_home(current_user.id)
