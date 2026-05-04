"""Teacher Tools worksheet HTTP routes."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.session import get_db
from app.domains.auth.dependencies import require_any_role
from app.domains.auth.models import User
from app.domains.teacher_worksheet.errors import WorksheetError
from app.domains.teacher_worksheet.models import TeacherWorksheet, TeacherWorksheetBlock, TeacherWorksheetSession
from app.domains.teacher_worksheet.repository import WorksheetListFilters
from app.domains.teacher_worksheet.schemas import (
    BlocksReorderRequest,
    DuplicateResponse,
    SessionsReorderRequest,
    WorksheetApiResponse,
    WorksheetBlockCreateRequest,
    WorksheetBlockPatchRequest,
    WorksheetBlockResponse,
    WorksheetCreateRequest,
    WorksheetGenerateRequest,
    WorksheetGenerateResponse,
    WorksheetListResponse,
    WorksheetPatchRequest,
    WorksheetSessionCreateRequest,
    WorksheetSessionPatchRequest,
    WorksheetSessionResponse,
)
from app.domains.teacher_worksheet.service import TeacherWorksheetService, _source_summary

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/teacher-tools", tags=["teacher-worksheet"])

_ALLOWED_ROLES = ("teacher", "school_admin", "super_admin", "org_admin")


def _topic_for_response(ws: TeacherWorksheet) -> str:
    return ws.topic_summary or "General scope"


def _block_to_response(b: TeacherWorksheetBlock) -> WorksheetBlockResponse:
    d = b.data if isinstance(b.data, dict) else {}
    return WorksheetBlockResponse(
        id=str(b.id),
        type=b.type,  # type: ignore[arg-type]
        prompt=b.prompt,
        points=float(b.points or 1.0),
        options=d.get("options"),
        answer=d.get("answer"),
        sampleAnswer=d.get("sample_answer"),
        responseLines=d.get("response_lines"),
        left=d.get("left"),
        right=d.get("right"),
    )


def _session_to_response(s: TeacherWorksheetSession) -> WorksheetSessionResponse:
    blocks = sorted(s.blocks or [], key=lambda x: x.sort_order)
    return WorksheetSessionResponse(
        id=str(s.id),
        sortOrder=int(s.sort_order),
        title=s.title,
        blocks=[_block_to_response(b) for b in blocks],
    )


def _to_worksheet_response(ws: TeacherWorksheet) -> WorksheetApiResponse:
    sessions = sorted(ws.sessions or [], key=lambda x: x.sort_order)
    return WorksheetApiResponse(
        id=str(ws.id),
        title=ws.title,
        subject=ws.subject,
        grade=ws.grade,
        outputFormat=ws.output_format,  # type: ignore[arg-type]
        classes=list(ws.class_keys or []),
        status=ws.status,  # type: ignore[arg-type]
        assignedAt=ws.assigned_at,
        dueAt=ws.due_at,
        sessions=[_session_to_response(s) for s in sessions],
        sessionsCount=int(ws.sessions_count or len(sessions)),
        blocksCount=int(ws.blocks_count or sum(len(list(s.blocks or [])) for s in sessions)),
        submissionCount=int(ws.submission_count or 0),
        avgScore=float(ws.avg_score or 0.0),
        topic=_topic_for_response(ws),
        sourceBookIds=[str(x) for x in (ws.source_pack_ids or [])],
        scopeTopics=list(ws.scope_topics or []),
        scopeRefinement=ws.scope_refinement,
        sourceSummary=_source_summary(ws),
        difficulty=ws.difficulty,
        handoutLayout=ws.handout_layout if isinstance(ws.handout_layout, dict) else None,
        studentInstructions=ws.student_instructions,
        teacherNotes=ws.teacher_notes,
        generateWithoutSources=bool(ws.generate_without_sources),
        createdAt=ws.created_at,
        updatedAt=ws.updated_at,
    )


def _raise_domain_error(e: WorksheetError) -> None:
    raise HTTPException(status_code=e.http_status, detail={"code": e.code, "message": e.message})


@router.get("/worksheets", response_model=WorksheetListResponse)
def list_worksheets(
    q: Optional[str] = None,
    subject: Optional[str] = None,
    grade: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    class_key: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_any_role(*_ALLOWED_ROLES)),
    db: Session = Depends(get_db),
) -> WorksheetListResponse:
    svc = TeacherWorksheetService(db)
    items, total = svc.list_worksheets(
        current_user=current_user,
        filters=WorksheetListFilters(
            q=q,
            subject=subject,
            grade=grade,
            status=status_filter,
            class_key=class_key,
            date_from=date_from,
            date_to=date_to,
        ),
        page=page,
        page_size=page_size,
    )
    return WorksheetListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[_to_worksheet_response(x) for x in items],
    )


@router.post("/worksheets", response_model=WorksheetApiResponse, status_code=status.HTTP_201_CREATED)
def create_worksheet(
    body: WorksheetCreateRequest,
    current_user: User = Depends(require_any_role(*_ALLOWED_ROLES)),
    db: Session = Depends(get_db),
) -> WorksheetApiResponse:
    svc = TeacherWorksheetService(db)
    ws = svc.create_worksheet(current_user=current_user, payload=body.model_dump(by_alias=True))
    return _to_worksheet_response(ws)


@router.get("/worksheets/{worksheet_id}", response_model=WorksheetApiResponse)
def get_worksheet(
    worksheet_id: UUID,
    current_user: User = Depends(require_any_role(*_ALLOWED_ROLES)),
    db: Session = Depends(get_db),
) -> WorksheetApiResponse:
    svc = TeacherWorksheetService(db)
    try:
        ws = svc.get_worksheet(current_user=current_user, worksheet_id=worksheet_id)
        return _to_worksheet_response(ws)
    except WorksheetError as e:
        _raise_domain_error(e)
        raise


@router.patch("/worksheets/{worksheet_id}", response_model=WorksheetApiResponse)
def patch_worksheet(
    worksheet_id: UUID,
    body: WorksheetPatchRequest,
    current_user: User = Depends(require_any_role(*_ALLOWED_ROLES)),
    db: Session = Depends(get_db),
) -> WorksheetApiResponse:
    svc = TeacherWorksheetService(db)
    try:
        ws = svc.patch_worksheet(current_user=current_user, worksheet_id=worksheet_id, patch=body.model_dump(exclude_unset=True, by_alias=True))
        return _to_worksheet_response(ws)
    except WorksheetError as e:
        _raise_domain_error(e)
        raise


@router.delete("/worksheets/{worksheet_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_worksheet(
    worksheet_id: UUID,
    current_user: User = Depends(require_any_role(*_ALLOWED_ROLES)),
    db: Session = Depends(get_db),
) -> Response:
    svc = TeacherWorksheetService(db)
    try:
        svc.delete_worksheet(current_user=current_user, worksheet_id=worksheet_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except WorksheetError as e:
        _raise_domain_error(e)
        raise


@router.post("/worksheets/{worksheet_id}/duplicate", response_model=DuplicateResponse)
def duplicate_worksheet(
    worksheet_id: UUID,
    current_user: User = Depends(require_any_role(*_ALLOWED_ROLES)),
    db: Session = Depends(get_db),
) -> DuplicateResponse:
    svc = TeacherWorksheetService(db)
    try:
        copy = svc.duplicate_worksheet(current_user=current_user, worksheet_id=worksheet_id)
        return DuplicateResponse(ok=True, id=str(copy.id))
    except WorksheetError as e:
        _raise_domain_error(e)
        raise


@router.post("/worksheets/{worksheet_id}/generate", response_model=WorksheetGenerateResponse)
async def generate_worksheet(
    worksheet_id: UUID,
    body: WorksheetGenerateRequest,
    response: Response,
    request: Request,
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
    current_user: User = Depends(require_any_role(*_ALLOWED_ROLES)),
    db: Session = Depends(get_db),
) -> WorksheetGenerateResponse:
    svc = TeacherWorksheetService(db)
    try:
        run, ws, warnings = await svc.generate_for_worksheet(
            current_user=current_user,
            worksheet_id=worksheet_id,
            req=body.model_dump(by_alias=True),
            idempotency_key=idempotency_key,
        )
        response.headers["X-Request-Id"] = request.headers.get("X-Request-Id", str(run.id))
        return WorksheetGenerateResponse(
            ok=True,
            generation_run_id=str(run.id),
            warnings=list(warnings),
            worksheet=_to_worksheet_response(ws),
        )
    except WorksheetError as e:
        _raise_domain_error(e)
        raise
    except Exception as e:
        logger.error("worksheet_generate_unexpected", exc_info=True)
        raise HTTPException(status_code=500, detail={"code": "INTERNAL_ERROR", "message": str(e)})


@router.post("/worksheets/{worksheet_id}/sessions", response_model=WorksheetApiResponse)
def add_session(
    worksheet_id: UUID,
    body: WorksheetSessionCreateRequest,
    current_user: User = Depends(require_any_role(*_ALLOWED_ROLES)),
    db: Session = Depends(get_db),
) -> WorksheetApiResponse:
    svc = TeacherWorksheetService(db)
    try:
        ws = svc.add_session(current_user=current_user, worksheet_id=worksheet_id, title=body.title)
        return _to_worksheet_response(ws)
    except WorksheetError as e:
        _raise_domain_error(e)
        raise


@router.patch("/worksheets/{worksheet_id}/sessions/{session_id}", response_model=WorksheetApiResponse)
def patch_session(
    worksheet_id: UUID,
    session_id: UUID,
    body: WorksheetSessionPatchRequest,
    current_user: User = Depends(require_any_role(*_ALLOWED_ROLES)),
    db: Session = Depends(get_db),
) -> WorksheetApiResponse:
    svc = TeacherWorksheetService(db)
    try:
        ws = svc.patch_session(
            current_user=current_user,
            worksheet_id=worksheet_id,
            session_id=session_id,
            patch=body.model_dump(exclude_unset=True),
        )
        return _to_worksheet_response(ws)
    except WorksheetError as e:
        _raise_domain_error(e)
        raise


@router.delete("/worksheets/{worksheet_id}/sessions/{session_id}", response_model=WorksheetApiResponse)
def delete_session(
    worksheet_id: UUID,
    session_id: UUID,
    current_user: User = Depends(require_any_role(*_ALLOWED_ROLES)),
    db: Session = Depends(get_db),
) -> WorksheetApiResponse:
    svc = TeacherWorksheetService(db)
    try:
        ws = svc.delete_session(current_user=current_user, worksheet_id=worksheet_id, session_id=session_id)
        return _to_worksheet_response(ws)
    except WorksheetError as e:
        _raise_domain_error(e)
        raise


@router.patch("/worksheets/{worksheet_id}/sessions/reorder", response_model=WorksheetApiResponse)
def reorder_sessions(
    worksheet_id: UUID,
    body: SessionsReorderRequest,
    current_user: User = Depends(require_any_role(*_ALLOWED_ROLES)),
    db: Session = Depends(get_db),
) -> WorksheetApiResponse:
    svc = TeacherWorksheetService(db)
    try:
        ws = svc.reorder_sessions(
            current_user=current_user,
            worksheet_id=worksheet_id,
            order=[item.model_dump() for item in body.order],
        )
        return _to_worksheet_response(ws)
    except WorksheetError as e:
        _raise_domain_error(e)
        raise


@router.post(
    "/worksheets/{worksheet_id}/sessions/{session_id}/blocks",
    response_model=WorksheetApiResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_block(
    worksheet_id: UUID,
    session_id: UUID,
    body: WorksheetBlockCreateRequest,
    current_user: User = Depends(require_any_role(*_ALLOWED_ROLES)),
    db: Session = Depends(get_db),
) -> WorksheetApiResponse:
    svc = TeacherWorksheetService(db)
    try:
        ws = svc.add_block(
            current_user=current_user,
            worksheet_id=worksheet_id,
            session_id=session_id,
            payload=body.model_dump(by_alias=True),
        )
        return _to_worksheet_response(ws)
    except WorksheetError as e:
        _raise_domain_error(e)
        raise


@router.patch(
    "/worksheets/{worksheet_id}/sessions/{session_id}/blocks/{block_id}",
    response_model=WorksheetApiResponse,
)
def patch_block(
    worksheet_id: UUID,
    session_id: UUID,
    block_id: UUID,
    body: WorksheetBlockPatchRequest,
    current_user: User = Depends(require_any_role(*_ALLOWED_ROLES)),
    db: Session = Depends(get_db),
) -> WorksheetApiResponse:
    svc = TeacherWorksheetService(db)
    try:
        ws = svc.patch_block(
            current_user=current_user,
            worksheet_id=worksheet_id,
            session_id=session_id,
            block_id=block_id,
            patch=body.model_dump(exclude_unset=True, by_alias=True),
        )
        return _to_worksheet_response(ws)
    except WorksheetError as e:
        _raise_domain_error(e)
        raise


@router.delete(
    "/worksheets/{worksheet_id}/sessions/{session_id}/blocks/{block_id}",
    response_model=WorksheetApiResponse,
)
def delete_block(
    worksheet_id: UUID,
    session_id: UUID,
    block_id: UUID,
    current_user: User = Depends(require_any_role(*_ALLOWED_ROLES)),
    db: Session = Depends(get_db),
) -> WorksheetApiResponse:
    svc = TeacherWorksheetService(db)
    try:
        ws = svc.delete_block(
            current_user=current_user,
            worksheet_id=worksheet_id,
            session_id=session_id,
            block_id=block_id,
        )
        return _to_worksheet_response(ws)
    except WorksheetError as e:
        _raise_domain_error(e)
        raise


@router.patch(
    "/worksheets/{worksheet_id}/sessions/{session_id}/blocks/reorder",
    response_model=WorksheetApiResponse,
)
def reorder_blocks(
    worksheet_id: UUID,
    session_id: UUID,
    body: BlocksReorderRequest,
    current_user: User = Depends(require_any_role(*_ALLOWED_ROLES)),
    db: Session = Depends(get_db),
) -> WorksheetApiResponse:
    svc = TeacherWorksheetService(db)
    try:
        ws = svc.reorder_blocks(
            current_user=current_user,
            worksheet_id=worksheet_id,
            session_id=session_id,
            order=[item.model_dump() for item in body.order],
        )
        return _to_worksheet_response(ws)
    except WorksheetError as e:
        _raise_domain_error(e)
        raise


@router.post(
    "/worksheets/{worksheet_id}/sessions/{session_id}/blocks/{block_id}/regenerate",
    response_model=WorksheetApiResponse,
)
async def regenerate_block(
    worksheet_id: UUID,
    session_id: UUID,
    block_id: UUID,
    current_user: User = Depends(require_any_role(*_ALLOWED_ROLES)),
    db: Session = Depends(get_db),
) -> WorksheetApiResponse:
    svc = TeacherWorksheetService(db)
    try:
        ws = await svc.regenerate_block(
            current_user=current_user,
            worksheet_id=worksheet_id,
            session_id=session_id,
            block_id=block_id,
        )
        return _to_worksheet_response(ws)
    except WorksheetError as e:
        _raise_domain_error(e)
        raise
    except Exception as e:
        logger.error("worksheet_block_regenerate_unexpected", exc_info=True)
        raise HTTPException(status_code=500, detail={"code": "INTERNAL_ERROR", "message": str(e)})
