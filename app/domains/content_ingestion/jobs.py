"""
Background jobs for content ingestion.
"""
import asyncio
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.session import SessionLocal
from app.domains.content_ingestion.services.ingestion_service import IngestionService

logger = get_logger(__name__)


async def ingest_document_job(document_id: UUID):
    """
    Background job to ingest a document through the processing pipeline.
    
    This function is designed to be called from FastAPI BackgroundTasks.
    For production, consider using Celery or similar task queue.
    
    Args:
        document_id: Document UUID to process
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting background ingestion job for document {document_id}")
        
        ingestion_service = IngestionService(db)
        document = await ingestion_service.ingest_document(document_id)
        
        logger.info(f"Background ingestion job completed for document {document_id}: {document.status}")
        
    except Exception as e:
        logger.error(f"Background ingestion job failed for document {document_id}: {e}", exc_info=True)
        # Update document status to failed with detailed error information
        try:
            from app.domains.content_ingestion.models import Document
            from app.domains.content_ingestion.enums import DocumentStatus
            document = db.query(Document).filter(Document.id == document_id).first()
            if document:
                document.status = DocumentStatus.FAILED.value
                document.error_code = "JOB_ERROR"
                
                # Provide more detailed error messages
                error_str = str(e)
                if "OPENAI_API_KEY" in error_str or "api key" in error_str.lower():
                    document.error_message = "OpenAI API key is missing or invalid. Please set OPENAI_API_KEY in .env file."
                    document.remediation_hint = "Set OPENAI_API_KEY in your .env file and restart the backend."
                elif "tesseract" in error_str.lower() or "ocr" in error_str.lower():
                    document.error_message = f"OCR processing failed: {error_str}"
                    document.remediation_hint = "Install Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki"
                elif "file not found" in error_str.lower() or "file_path" in error_str.lower():
                    document.error_message = f"Document file not found: {error_str}"
                    document.remediation_hint = "The uploaded file may have been deleted or moved. Try re-uploading."
                elif "embedding" in error_str.lower():
                    document.error_message = f"Embedding generation failed: {error_str}"
                    document.remediation_hint = "Check OPENAI_API_KEY and network connectivity."
                elif "vector" in error_str.lower() or "pgvector" in error_str.lower():
                    document.error_message = f"Vector storage failed: {error_str}"
                    document.remediation_hint = "Check database connection and pgvector extension."
                else:
                    document.error_message = error_str
                    document.remediation_hint = "Check backend logs for detailed error information."
                
                db.commit()
                logger.info(f"Updated document {document_id} status to FAILED with error: {document.error_message}")
        except Exception as commit_error:
            logger.error(f"Failed to update document status: {commit_error}", exc_info=True)
    finally:
        db.close()


def run_ingestion_job_sync(document_id: UUID):
    """
    Synchronous wrapper for ingestion job (FastAPI BackgroundTasks).

    Tasks run in a worker thread without a running asyncio loop; use asyncio.run.
    Avoid get_event_loop/create_task patterns — they caused duplicate or orphaned tasks.
    """
    asyncio.run(ingest_document_job(document_id))
