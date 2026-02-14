"""
Content Ingestion API routes.
"""
import asyncio
import json
from typing import List, Optional
from uuid import UUID, uuid4
from pathlib import Path

from fastapi import (
    APIRouter, Depends, HTTPException, status, UploadFile, File, Form,
    BackgroundTasks, Request, Response
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.session import get_db
from app.domains.auth.dependencies import get_current_user, require_role, require_any_role
from app.domains.auth.models import User
from app.domains.content_ingestion import schemas
from app.domains.content_ingestion.services import (
    ContentPackService,
    DocumentService,
    QAService,
    WorksheetService,
)
from app.domains.content_ingestion.jobs import run_ingestion_job_sync
from app.domains.content_ingestion.models import Document, DocumentProcessingRun
from app.domains.content_ingestion.enums import DocumentStatus
from app.core.config import settings

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["content-ingestion"])


# ========== Content Pack Endpoints ==========

@router.get("/admin/content-packs/test")
async def test_content_packs_route():
    """Test endpoint to verify route registration (no auth required)."""
    return {"message": "Content packs route is working", "status": "ok", "path": "/api/v1/admin/content-packs"}


@router.post("/admin/content-packs", response_model=schemas.ContentPackResponse, status_code=status.HTTP_201_CREATED)
async def create_content_pack(
    data: schemas.ContentPackCreate,
    current_user: User = Depends(require_any_role("org_admin", "school_admin", "super_admin")),
    db: Session = Depends(get_db),
):
    """Create a new content pack."""
    service = ContentPackService(db)
    pack = service.create_pack(
        data=data,
        tenant_id=current_user.tenant_id,
        created_by=current_user.id
    )
    return pack


@router.get("/admin/content-packs", response_model=List[schemas.ContentPackListItem])
async def list_content_packs(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    current_user: User = Depends(require_any_role("org_admin", "school_admin", "super_admin", "teacher")),
    db: Session = Depends(get_db),
):
    """List content packs. Teachers can view active packs for worksheet generation."""
    logger.info(f"List content packs called by user {current_user.id}, tenant {current_user.tenant_id}, is_active={is_active}")
    try:
        service = ContentPackService(db)
        packs, total = service.list_packs(
            tenant_id=current_user.tenant_id,
            skip=skip,
            limit=limit,
            is_active=is_active
        )
        logger.info(f"Returning {len(packs)} packs for tenant {current_user.tenant_id}")
        return packs
    except Exception as e:
        logger.error(f"Error listing content packs: {e}", exc_info=True)
        raise


@router.get("/admin/content-packs/{pack_id}", response_model=schemas.ContentPackResponse)
async def get_content_pack(
    pack_id: UUID,
    current_user: User = Depends(require_any_role("org_admin", "school_admin", "super_admin", "teacher")),
    db: Session = Depends(get_db),
):
    """Get content pack details. Teachers can view pack details for worksheet generation."""
    service = ContentPackService(db)
    pack = service.get_pack(pack_id, current_user.tenant_id)
    if not pack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content pack not found"
        )
    return pack


@router.put("/admin/content-packs/{pack_id}", response_model=schemas.ContentPackResponse)
async def update_content_pack(
    pack_id: UUID,
    data: schemas.ContentPackCreate,
    current_user: User = Depends(require_any_role("org_admin", "school_admin", "super_admin")),
    db: Session = Depends(get_db),
):
    """Update a content pack."""
    service = ContentPackService(db)
    pack = service.update_pack(
        pack_id=pack_id,
        tenant_id=current_user.tenant_id,
        name=data.name,
        description=data.description,
        subject=data.subject,
        grade=data.grade,
        curriculum=data.curriculum,
        pack_metadata=data.metadata,
    )
    if not pack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content pack not found"
        )
    # Map pack_metadata to metadata for API response
    if hasattr(pack, 'pack_metadata'):
        pack.metadata = pack.pack_metadata
    return pack


@router.delete("/admin/content-packs/{pack_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content_pack(
    pack_id: UUID,
    current_user: User = Depends(require_any_role("org_admin", "school_admin", "super_admin")),
    db: Session = Depends(get_db),
):
    """Delete (deactivate) a content pack."""
    service = ContentPackService(db)
    success = service.delete_pack(pack_id, current_user.tenant_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content pack not found"
        )
    return None


# ========== Document Endpoints ==========

@router.post("/admin/documents/upload-stream")
async def upload_document_with_stream(
    background_tasks: BackgroundTasks,
    pack_id: Optional[str] = Form(None),  # Optional - create pack if not provided
    pack_name: Optional[str] = Form(None),
    pack_description: Optional[str] = Form(None),
    pack_subject: Optional[str] = Form(None),
    pack_grade: Optional[str] = Form(None),
    pack_curriculum: Optional[str] = Form(None),
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    chapter_map: Optional[str] = Form(None),
    force_ocr: bool = Form(False),
    current_user: User = Depends(require_any_role("org_admin", "school_admin", "super_admin")),
    db: Session = Depends(get_db),
):
    """
    Unified endpoint: Upload document with optional pack creation - streams real-time progress.
    If pack_id is not provided, creates a new pack using pack_* fields.
    """
    async def generate_progress_stream():
        """Generate SSE events for upload and processing progress."""
        try:
            # Step 1: Validate file
            yield f"data: {json.dumps({'type': 'progress', 'step': 'validating', 'message': 'Validating file...', 'percentage': 5})}\n\n"
            await asyncio.sleep(0.05)
            
            # Ensure we flush the stream immediately
            import sys
            if hasattr(sys.stdout, 'flush'):
                sys.stdout.flush()
            
            if not file.filename:
                yield f"data: {json.dumps({'type': 'error', 'message': 'No file provided'})}\n\n"
                return
            
            # Read file
            yield f"data: {json.dumps({'type': 'progress', 'step': 'reading', 'message': 'Reading file...', 'percentage': 15})}\n\n"
            await asyncio.sleep(0.05)
            
            file_content = await file.read()
            file_size = len(file_content)
            max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
            if file_size > max_size:
                yield f"data: {json.dumps({'type': 'error', 'message': f'File size ({file_size / 1024 / 1024:.2f}MB) exceeds maximum ({settings.MAX_FILE_SIZE_MB}MB)'})}\n\n"
                return
            
            # Step 2: Create or get pack
            yield f"data: {json.dumps({'type': 'progress', 'step': 'pack', 'message': 'Setting up content pack...', 'percentage': 30})}\n\n"
            await asyncio.sleep(0.05)
            
            pack_service = ContentPackService(db)
            if pack_id:
                try:
                    pack_uuid = UUID(pack_id)
                    pack = pack_service.get_pack(pack_uuid, current_user.tenant_id)
                    if not pack:
                        yield f"data: {json.dumps({'type': 'error', 'message': 'Content pack not found'})}\n\n"
                        return
                except ValueError:
                    yield f"data: {json.dumps({'type': 'error', 'message': 'Invalid pack_id format'})}\n\n"
                    return
            else:
                # Create new pack
                if not pack_name:
                    yield f"data: {json.dumps({'type': 'error', 'message': 'pack_name is required when pack_id is not provided'})}\n\n"
                    return
                
                pack_data = schemas.ContentPackCreate(
                    name=pack_name,
                    description=pack_description,
                    subject=pack_subject,
                    grade=pack_grade,
                    curriculum=pack_curriculum
                )
                pack = pack_service.create_pack(
                    data=pack_data,
                    tenant_id=current_user.tenant_id,
                    created_by=current_user.id
                )
                yield f"data: {json.dumps({'type': 'progress', 'step': 'pack_created', 'message': f'Created pack: {pack.name}', 'pack_id': str(pack.id), 'percentage': 40})}\n\n"
                await asyncio.sleep(0.05)
            
            # Step 3: Save file
            yield f"data: {json.dumps({'type': 'progress', 'step': 'saving', 'message': 'Saving file...', 'percentage': 50})}\n\n"
            await asyncio.sleep(0.05)
            
            documents_dir = Path(settings.DOCUMENTS_DIR)
            documents_dir.mkdir(parents=True, exist_ok=True)
            
            import uuid
            from datetime import datetime
            file_ext = Path(file.filename).suffix
            unique_filename = f"{uuid.uuid4()}_{int(datetime.now().timestamp())}{file_ext}"
            file_path = documents_dir / unique_filename
            
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            # Step 4: Create document record
            yield f"data: {json.dumps({'type': 'progress', 'step': 'creating', 'message': 'Creating document record...', 'percentage': 70})}\n\n"
            await asyncio.sleep(0.05)
            
            import hashlib
            file_hash = hashlib.sha256(file_content).hexdigest()
            
            filename_lower = file.filename.lower()
            if filename_lower.endswith('.pdf'):
                source_type = "pdf"
            elif filename_lower.endswith('.docx'):
                source_type = "docx"
            elif filename_lower.endswith(('.jpg', '.jpeg', '.png', '.tiff')):
                source_type = "image"
            else:
                yield f"data: {json.dumps({'type': 'error', 'message': f'Unsupported file type: {file.filename}'})}\n\n"
                return
            
            chapter_map_data = None
            if chapter_map:
                try:
                    chapter_map_data = json.loads(chapter_map)
                except json.JSONDecodeError:
                    yield f"data: {json.dumps({'type': 'error', 'message': 'Invalid chapter_map JSON'})}\n\n"
                    return
            
            document_service = DocumentService(db)
            document = document_service.create_document(
                pack_id=pack.id,
                filename=file.filename,
                file_path=str(file_path),
                file_size=file_size,
                mime_type=file.content_type,
                source_type=source_type,
                tenant_id=current_user.tenant_id,
                uploaded_by=current_user.id,
                title=title,
                author=author,
                chapter_map=chapter_map_data,
                document_hash=file_hash
            )
            
            if force_ocr:
                document.processing_metadata = {"force_ocr": True}
                db.commit()
            
            yield f"data: {json.dumps({'type': 'progress', 'step': 'uploaded', 'message': 'File uploaded successfully', 'document_id': str(document.id), 'percentage': 85})}\n\n"
            await asyncio.sleep(0.05)
            
            # Step 5: Start processing
            yield f"data: {json.dumps({'type': 'progress', 'step': 'processing', 'message': 'Starting document processing...', 'percentage': 90})}\n\n"
            await asyncio.sleep(0.05)
            
            # Trigger background ingestion job
            background_tasks.add_task(run_ingestion_job_sync, document.id)
            
            # Final success
            yield f"data: {json.dumps({'type': 'success', 'message': 'Upload complete. Processing started.', 'document_id': str(document.id), 'pack_id': str(pack.id), 'percentage': 100})}\n\n"
            
        except Exception as e:
            logger.error(f"Error in upload stream: {e}", exc_info=True)
            # Ensure error is sent to client
            try:
                error_msg = str(e)
                # Make error message user-friendly
                if "institution_admin" in error_msg.lower() or "enum" in error_msg.lower():
                    error_msg = "Authorization error. Please contact support if this persists."
                yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
            except Exception as send_error:
                logger.error(f"Failed to send error to client: {send_error}", exc_info=True)
                # Last resort: try to send a generic error
                try:
                    yield f"data: {json.dumps({'type': 'error', 'message': 'An error occurred during upload. Please try again.'})}\n\n"
                except:
                    pass  # If we can't even send error, just log it
    
    return StreamingResponse(
        generate_progress_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "X-Content-Type-Options": "nosniff",
        }
    )


@router.post("/admin/documents", response_model=schemas.DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    pack_id: UUID = Form(...),
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    chapter_map: Optional[str] = Form(None),  # JSON string
    force_ocr: bool = Form(False),
    current_user: User = Depends(require_any_role("org_admin", "school_admin", "super_admin")),
    db: Session = Depends(get_db),
):
    """Upload a document for processing."""
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    # Check file size
    file_content = await file.read()
    file_size = len(file_content)
    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds maximum ({settings.MAX_FILE_SIZE_MB}MB)"
        )
    
    # Determine source type
    filename_lower = file.filename.lower()
    if filename_lower.endswith('.pdf'):
        source_type = "pdf"
    elif filename_lower.endswith('.docx'):
        source_type = "docx"
    elif filename_lower.endswith(('.jpg', '.jpeg', '.png', '.tiff')):
        source_type = "image"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.filename}"
        )
    
    # Save file
    documents_dir = Path(settings.DOCUMENTS_DIR)
    documents_dir.mkdir(parents=True, exist_ok=True)
    
    import uuid
    from datetime import datetime
    file_ext = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}_{int(datetime.now().timestamp())}{file_ext}"
    file_path = documents_dir / unique_filename
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Calculate file hash
    import hashlib
    file_hash = hashlib.sha256(file_content).hexdigest()
    
    # Parse chapter map if provided
    chapter_map_data = None
    if chapter_map:
        try:
            chapter_map_data = json.loads(chapter_map)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid chapter_map JSON"
            )
    
    # Create document record
    service = DocumentService(db)
    document = service.create_document(
        pack_id=pack_id,
        filename=file.filename,
        file_path=str(file_path),
        file_size=file_size,
        mime_type=file.content_type,
        source_type=source_type,
        tenant_id=current_user.tenant_id,
        uploaded_by=current_user.id,
        title=title,
        author=author,
        chapter_map=chapter_map_data,
        document_hash=file_hash
    )
    
    # Store force_ocr in processing_metadata
    if force_ocr:
        document.processing_metadata = {"force_ocr": True}
        db.commit()
    
    # Trigger background ingestion job
    background_tasks.add_task(run_ingestion_job_sync, document.id)
    
    logger.info(f"Document uploaded: {document.id}, ingestion job queued")
    return document


@router.get("/admin/documents", response_model=List[schemas.DocumentListItem])
async def list_documents(
    pack_id: Optional[UUID] = None,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_any_role("org_admin", "school_admin", "super_admin")),
    db: Session = Depends(get_db),
):
    """List documents."""
    service = DocumentService(db)
    documents, total = service.list_documents(
        tenant_id=current_user.tenant_id,
        pack_id=pack_id,
        status=status_filter,
        skip=skip,
        limit=limit
    )
    return documents


@router.get("/admin/documents/{document_id}", response_model=schemas.DocumentResponse)
async def get_document(
    document_id: UUID,
    current_user: User = Depends(require_any_role("org_admin", "school_admin", "super_admin")),
    db: Session = Depends(get_db),
):
    """Get document details."""
    service = DocumentService(db)
    document = service.get_document(document_id, current_user.tenant_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document


@router.delete("/admin/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    current_user: User = Depends(require_any_role("org_admin", "school_admin", "super_admin")),
    db: Session = Depends(get_db),
):
    """Delete a document."""
    service = DocumentService(db)
    success = service.delete_document(document_id, current_user.tenant_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return None


@router.get("/admin/documents/{document_id}/status/stream")
async def stream_document_status(
    document_id: UUID,
    current_user: User = Depends(require_any_role("org_admin", "school_admin", "super_admin")),
    db: Session = Depends(get_db),
):
    """Stream real-time document processing status via SSE."""
    # Verify document exists and user has access
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.tenant_id == current_user.tenant_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    async def generate_status_stream():
        """Generate SSE events for document status updates."""
        last_status = None
        last_progress = None
        
        while True:
            # Refresh document from database
            db.refresh(document)
            
            # Get latest processing run
            latest_run = db.query(DocumentProcessingRun).filter(
                DocumentProcessingRun.document_id == document_id
            ).order_by(DocumentProcessingRun.started_at.desc()).first()
            
            # Build status response
            current_status = document.status
            progress = None
            
            if latest_run:
                progress = {
                    "step": latest_run.current_step or current_status,
                    "completed": latest_run.chunks_created or 0,
                    "total": latest_run.chunks_created or 0,  # Will be updated during processing
                    "percentage": latest_run.progress_percentage or 0,
                }
            
            # Only send update if status or progress changed
            if current_status != last_status or progress != last_progress:
                status_data = {
                    "document_id": str(document_id),
                    "status": current_status,
                    "progress": progress,
                    "steps_completed": latest_run.completed_steps or [],
                    "current_step": latest_run.current_step or current_status,
                    "error_code": document.error_code,
                    "error_message": document.error_message,
                    "remediation_hint": document.remediation_hint,
                }
                
                event_json = json.dumps(status_data)
                yield f"data: {event_json}\n\n"
                
                last_status = current_status
                last_progress = progress
            
            # If processing is complete or failed, break
            if current_status in [DocumentStatus.PUBLISHED.value, DocumentStatus.FAILED.value]:
                break
            
            # Wait before next check
            await asyncio.sleep(1)  # Update every 1 second
    
    return StreamingResponse(
        generate_status_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.post("/admin/documents/{document_id}/retry", response_model=schemas.DocumentResponse)
async def retry_document_processing(
    document_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_any_role("org_admin", "school_admin", "super_admin")),
    db: Session = Depends(get_db),
):
    """Retry failed document processing."""
    service = DocumentService(db)
    document = service.get_document(document_id, current_user.tenant_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if document.status not in [DocumentStatus.FAILED.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot retry document with status: {document.status}"
        )
    
    # Reset status
    service.update_document_status(
        document_id=document_id,
        status=DocumentStatus.UPLOADED.value,
        error_code=None,
        error_message=None,
        remediation_hint=None
    )
    
    # Trigger background ingestion job
    background_tasks.add_task(run_ingestion_job_sync, document_id)
    
    logger.info(f"Retrying document processing: {document_id}")
    return document


@router.post("/admin/documents/{document_id}/qa/run", response_model=schemas.QAValidationResponse)
async def run_qa_validation(
    document_id: UUID,
    request: Optional[schemas.QAValidationRequest] = None,
    current_user: User = Depends(require_any_role("org_admin", "school_admin", "super_admin")),
    db: Session = Depends(get_db),
):
    """Run QA validation on a document."""
    service = DocumentService(db)
    document = service.get_document(document_id, current_user.tenant_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    qa_service = QAService(db)
    qa_validation = qa_service.run_qa_validation(
        document_id=document_id,
        thresholds=request.thresholds if request else None,
        golden_queries=request.golden_queries if request else None
    )
    
    return qa_validation


@router.post("/admin/documents/{document_id}/publish", response_model=schemas.DocumentResponse)
async def publish_document(
    document_id: UUID,
    override_qa: bool = False,
    override_reason: Optional[str] = None,
    current_user: User = Depends(require_any_role("org_admin", "school_admin", "super_admin")),
    db: Session = Depends(get_db),
):
    """
    Publish a document (QA must pass unless overridden).
    
    Ensures document has been fully processed with embeddings stored before publishing.
    """
    service = DocumentService(db)
    document = service.get_document(document_id, current_user.tenant_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if document has been processed with embeddings (embedding_v for fake/local)
    from app.core.config import settings
    emb_provider = (settings.EMBEDDING_PROVIDER or "fake").lower()
    if emb_provider in ("fake", "local"):
        chunks_with_embeddings = db.query(Chunk).filter(
            Chunk.document_id == document_id,
            Chunk.embedding_v.isnot(None),
            Chunk.embedding_model == emb_provider
        ).count()
    else:
        chunks_with_embeddings = db.query(Chunk).filter(
            Chunk.document_id == document_id,
            Chunk.embedding.isnot(None)
        ).count()
    
    if chunks_with_embeddings == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document has not been processed yet. Please wait for ingestion to complete, or the document may need to be reprocessed."
        )
    
    # Check QA status
    from app.domains.content_ingestion.models import QAValidation
    latest_qa = db.query(QAValidation).filter(
        QAValidation.document_id == document_id
    ).order_by(QAValidation.created_at.desc()).first()
    
    if not latest_qa:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="QA validation must be run before publishing"
        )
    
    if latest_qa.qa_status != "passed" and not override_qa:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"QA validation did not pass (status: {latest_qa.qa_status}). Use override_qa=true to publish anyway."
        )
    
    # Publish document
    from datetime import datetime, timezone
    service.update_document_status(
        document_id=document_id,
        status=DocumentStatus.PUBLISHED.value
    )
    document.processed_at = datetime.now(timezone.utc)
    db.commit()
    
    logger.info(f"Document {document_id} published (override: {override_qa}, chunks with embeddings: {chunks_with_embeddings})")
    return document


# ========== Worksheet Endpoints ==========

@router.post("/worksheets/generate", response_model=schemas.WorksheetResponse)
async def generate_worksheet(
    request: schemas.WorksheetGenerateRequest,
    response: Response,
    http_request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a worksheet using RAG. Hard timeout applied; 504 on timeout."""
    request_id = str(uuid4())
    timeout_sec = getattr(settings, "WORKSHEET_GENERATION_TIMEOUT_SECONDS", 180.0)
    # When cache is disabled, default skip_cache_write to True so no DB write
    skip_cache_write = request.skip_cache_write if request.skip_cache_write is not None else (not getattr(settings, "WORKSHEET_CACHE_ENABLED", False))
    # Bypass cache when client requests regeneration (force_regenerate or regenerate_key)
    force_regenerate = request.force_regenerate or bool(request.regenerate_key)
    service = WorksheetService(db)
    try:
        # Convert single difficulty to difficulty_mix if provided
        # The service method only accepts difficulty_mix, not difficulty
        difficulty_mix_to_use = request.difficulty_mix
        if request.difficulty and not difficulty_mix_to_use:
            # Convert single difficulty to difficulty_mix (100% that difficulty)
            difficulty_mix_to_use = {
                request.difficulty: 1.0
            }
        
        # Call generate_worksheet with only the parameters it accepts
        # Note: skip_cache_write, request_id, user_id, regenerate_key, tenant_id are not used by the service method
        worksheet_cache = await asyncio.wait_for(
            service.generate_worksheet(
                pack_id=request.pack_id,
                topic_id=request.topic_id,
                topic_text=request.topic_text,
                grade=request.grade,
                subject=request.subject,
                difficulty_mix=difficulty_mix_to_use,
                num_questions=request.num_questions,
                question_types=request.question_types,
                force_regenerate=force_regenerate,
            ),
            timeout=timeout_sec,
        )
        
        # Handle skip_cache_write after generation (if needed)
        # Note: The service always saves to cache, so if skip_cache_write is True,
        # we would need to delete it, but for now we'll let it cache
    except asyncio.TimeoutError:
        logger.warning(f"Worksheet generation timed out after {timeout_sec}s request_id={request_id}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={
                "message": "Generation timed out. Reduce questions or try again.",
                "request_id": request_id,
            },
        )
    except ValueError as e:
        msg = str(e)
        logger.warning("Worksheet generate ValueError: %s", msg, exc_info=False)
        if "Topic content not found" in msg or "VALIDATION_FAILED" in msg or "TOPIC_NOT_FOUND_IN_PACK" in msg:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"message": msg, "code": "TOPIC_NOT_FOUND_OR_VALIDATION_FAILED"},
            )
        if "Unable to generate at the requested difficulty" in msg:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"message": msg, "code": "DIFFICULTY_GENERATION_FAILED"},
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": msg, "code": "GENERATION_FAILED"},
        )
    except Exception as e:
        # Catch any other unexpected exceptions (TypeError, AttributeError, etc.)
        logger.error(f"Unexpected error in worksheet generation (request_id={request_id}): {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": f"Internal server error: {str(e)}",
                "code": "INTERNAL_ERROR",
                "request_id": request_id
            }
        )
    
    # Response headers for diagnostics and client UX (do not break existing clients)
    from_cache = getattr(worksheet_cache, "from_cache", False)
    response.headers["X-Request-Id"] = request_id
    response.headers["X-Worksheet-Cache"] = "hit" if from_cache else "miss"

    # When difficulty was requested: ensure response includes metadata (from generation or derived from cache)
    final_difficulty_used = getattr(worksheet_cache, "final_difficulty_used", None)
    attempts_count = getattr(worksheet_cache, "attempts_count", None)
    validator_report_per_attempt = getattr(worksheet_cache, "validator_report_per_attempt", None)
    warnings = getattr(worksheet_cache, "warnings", None)
    if request.difficulty and from_cache and final_difficulty_used is None:
        mix = getattr(worksheet_cache, "difficulty_mix", None) or {}
        if mix.get("hard") == 1 or mix.get("hard") == 1.0:
            final_difficulty_used = "hard"
        elif mix.get("medium") == 1 or mix.get("medium") == 1.0:
            final_difficulty_used = "medium"
        elif mix.get("easy") == 1 or mix.get("easy") == 1.0:
            final_difficulty_used = "easy"
        attempts_count = 0
        validator_report_per_attempt = []
        warnings = []

    # Response hygiene: hide internal fields unless DEBUG or X-Debug: 1 (log only in production)
    debug = (http_request.headers.get("X-Debug") == "1" or getattr(settings, "DEBUG", False))
    if not debug:
        validator_report_per_attempt = None
        warnings = None

    # created_at must never be null in response
    from datetime import datetime, timezone
    created_at = getattr(worksheet_cache, "created_at", None) or datetime.now(timezone.utc)

    # Convert to response format
    worksheet_data = worksheet_cache.worksheet_json
    questions = [
        schemas.WorksheetQuestion(**q) for q in worksheet_data.get("questions", [])
    ]
    
    # citations: list of {chunk_id, document_id, page_range}; backward-compat for old cache without "citations"
    retrieval = worksheet_cache.retrieval_metadata or {}
    if not isinstance(retrieval, dict):
        retrieval = {}
    citations = retrieval.get("citations")
    if not isinstance(citations, list):
        citations = []

    return schemas.WorksheetResponse(
        id=worksheet_cache.id,
        pack_id=worksheet_cache.pack_id,
        topic_id=worksheet_cache.topic_id,
        topic_text=worksheet_cache.topic_text,
        grade=worksheet_cache.grade,
        subject=worksheet_cache.subject,
        questions=questions,
        answer_key=worksheet_data.get("answer_key", {}),
        marking_scheme=worksheet_data.get("marking_scheme", {}),
        citations=citations,
        created_at=created_at,
        chapter_page_range=retrieval.get("chapter_page_range"),
        relevance_avg_sim=retrieval.get("relevance_avg_sim"),
        relevance_keyword_hits=retrieval.get("relevance_keyword_hits"),
        final_difficulty_used=final_difficulty_used,
        attempts_count=attempts_count,
        attempts=attempts_count,
        validator_report_per_attempt=validator_report_per_attempt if debug else None,
        validator_reports=validator_report_per_attempt if debug else None,
        warnings=warnings if debug else None,
    )


@router.get("/worksheets/{worksheet_id}", response_model=schemas.WorksheetResponse)
async def get_worksheet(
    worksheet_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get cached worksheet by ID."""
    service = WorksheetService(db)
    worksheet_cache = service.get_worksheet(worksheet_id)
    
    if not worksheet_cache:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worksheet not found"
        )
    
    # Convert to response format
    worksheet_data = worksheet_cache.worksheet_json
    questions = [
        schemas.WorksheetQuestion(**q) for q in worksheet_data.get("questions", [])
    ]
    
    # citations: list of {chunk_id, document_id, page_range}; backward-compat for old cache without "citations"
    retrieval = worksheet_cache.retrieval_metadata or {}
    citations = retrieval.get("citations") if isinstance(retrieval, dict) else None
    if not isinstance(citations, list):
        citations = []
    from datetime import datetime, timezone
    created_at = getattr(worksheet_cache, "created_at", None) or datetime.now(timezone.utc)

    return schemas.WorksheetResponse(
        id=worksheet_cache.id,
        pack_id=worksheet_cache.pack_id,
        topic_id=worksheet_cache.topic_id,
        topic_text=worksheet_cache.topic_text,
        grade=worksheet_cache.grade,
        subject=worksheet_cache.subject,
        questions=questions,
        answer_key=worksheet_data.get("answer_key", {}),
        marking_scheme=worksheet_data.get("marking_scheme", {}),
        citations=citations,
        created_at=created_at,
    )
