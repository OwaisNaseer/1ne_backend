"""
Document ingestion service - main pipeline orchestrator.
Provider-driven; checkpoints and observability; free mode supported.
"""
import os
import hashlib
import time
from typing import Optional, Dict, Any, List
from uuid import UUID
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.config import settings
from app.domains.content_ingestion.models import (
    Document, PageText, Chunk, DocumentProcessingRun
)
from app.domains.content_ingestion.enums import DocumentStatus
from app.domains.content_ingestion.detection import (
    detect_mime_and_source,
    classify_pdf_after_extract,
)
from app.domains.content_ingestion.providers.ocr_providers import (
    TesseractOCRProvider,
    EasyOCRProvider,
    MathpixOCRProvider,
)
from app.domains.content_ingestion.providers.text_extractors import (
    PDFTextExtractor,
    DOCXTextExtractor,
)
from app.domains.content_ingestion.providers.chunkers import SimpleChunker
from app.domains.content_ingestion.providers.embedding_providers import (
    FakeEmbeddingProvider,
    LocalSentenceTransformersEmbeddingProvider,
    OpenAIEmbeddingProvider,
)
from app.domains.content_ingestion.providers.vector_stores import PgVectorStore
from app.domains.content_ingestion.providers.math_providers import (
    BaselineMathExtractionProvider,
    compute_math_density,
)
from app.domains.content_ingestion.providers.ocr_preflight import OcrPreflight, OcrPreflightError

logger = get_logger(__name__)
MATH_DENSITY_THRESHOLD = 0.5  # per-page threshold for content_type_hint=math


class IngestionService:
    """Service for ingesting documents through the processing pipeline."""
    
    def __init__(self, db: Session):
        """Initialize ingestion service."""
        self.db = db
        self._init_providers()
    
    def _init_providers(self):
        """Initialize providers based on configuration."""
        # OCR provider
        if settings.OCR_ENGINE == "tesseract":
            self.ocr_provider = TesseractOCRProvider()
        elif settings.OCR_ENGINE == "easyocr":
            self.ocr_provider = EasyOCRProvider()
        elif settings.OCR_ENGINE == "mathpix":
            self.ocr_provider = MathpixOCRProvider()
        else:
            self.ocr_provider = TesseractOCRProvider()
        
        # Text extractors
        self.pdf_extractor = PDFTextExtractor()
        self.docx_extractor = DOCXTextExtractor()
        
        # Chunker
        self.chunker = SimpleChunker()
        
        # Embedding provider (config-only)
        emb = (settings.EMBEDDING_PROVIDER or "fake").lower()
        if emb == "openai":
            self.embedding_provider = OpenAIEmbeddingProvider()
        elif emb == "local":
            self.embedding_provider = LocalSentenceTransformersEmbeddingProvider()
        else:
            self.embedding_provider = FakeEmbeddingProvider()
        
        # Vector store
        if settings.VECTOR_STORE == "pgvector":
            self.vector_store = PgVectorStore(db=self.db)
        else:
            self.vector_store = PgVectorStore(db=self.db)
        # Math provider (config: MATH_PROVIDER=baseline|mathpix)
        if getattr(settings, "MATH_PROVIDER", "baseline") == "baseline":
            self.math_provider = BaselineMathExtractionProvider()
        else:
            self.math_provider = BaselineMathExtractionProvider()
    
    async def ingest_document(self, document_id: UUID) -> Document:
        """
        Main ingestion pipeline for a document.
        
        State machine:
        UPLOADED -> TEXT_EXTRACTING -> OCR_RUNNING (conditional) 
        -> NORMALIZING -> CHUNKING -> EMBEDDING -> INDEXING 
        -> QA_VALIDATION -> PUBLISHED
        """
        document = self.db.query(Document).filter(
            Document.id == document_id
        ).first()
        
        if not document:
            raise ValueError(f"Document {document_id} not found")
        if not os.path.exists(document.file_path):
            raise FileNotFoundError(f"Document file not found: {document.file_path}")

        # File type / MIME detection at ingestion start
        detected_mime, detected_source_type, pdf_type_initial, extraction_strategy = detect_mime_and_source(
            file_path=document.file_path,
            filename=document.filename,
        )
        meta = dict(document.processing_metadata or {})
        meta["detected_mime"] = detected_mime
        meta["detected_source_type"] = detected_source_type
        meta["extraction_strategy"] = extraction_strategy
        if pdf_type_initial:
            meta["pdf_type"] = pdf_type_initial
        document.processing_metadata = meta
        self.db.commit()
        logger.info(
            "ingestion_start",
            extra={
                "document_id": str(document_id),
                "detected_mime": detected_mime,
                "detected_source_type": detected_source_type,
                "extraction_strategy": extraction_strategy,
            },
        )

        logger.info(f"Starting ingestion pipeline for document {document_id}")
        
        # Create processing run
        processing_run = DocumentProcessingRun(
            document_id=document_id,
            status=DocumentStatus.TEXT_EXTRACTING.value,
            current_step="text_extracting"
        )
        self.db.add(processing_run)
        self.db.commit()
        
        try:
            # Step 1: Text Extraction
            t0 = time.perf_counter()
            await self._update_status(document_id, DocumentStatus.TEXT_EXTRACTING.value, processing_run)
            pages = await self._extract_text(document)
            duration_ms = int((time.perf_counter() - t0) * 1000)
            logger.info(
                "step_complete",
                extra={"document_id": str(document_id), "step": "text_extracting", "duration_ms": duration_ms, "pages": len(pages) if pages else 0},
            )
            if not pages:
                raise ValueError("No text extracted from document")
            
            # PDF: classify digital vs scanned after extract (before OCR decision)
            if document.source_type == "pdf" and pages:
                pdf_type = classify_pdf_after_extract(
                    [p.char_count for p in pages],
                    threshold_chars=getattr(settings, "SCANNED_THRESHOLD_CHARS", 50),
                )
                meta = dict(document.processing_metadata or {})
                meta["pdf_type"] = pdf_type
                meta["extraction_strategy"] = "ocr" if pdf_type == "scanned" else "pdf_text"
                document.processing_metadata = meta
                self.db.commit()
            
            # Store initial page texts (may be updated by OCR)
            for page in pages:
                page_text = PageText(
                    document_id=document_id,
                    page_no=page.page_no,
                    text=page.text,
                    char_count=page.char_count,
                    ocr_confidence=page.ocr_confidence,
                    ocr_engine=page.ocr_engine
                )
                self.db.add(page_text)
            
            self.db.commit()
            
            # Update document total pages
            document.total_pages = len(pages)
            self.db.commit()
            
            processing_run.pages_processed = len(pages)
            self.db.commit()
            
            # Step 2: OCR (if needed)
            # Check if OCR is needed: total_chars==0 OR avg_chars<threshold OR force_ocr
            total_chars = sum(p.char_count for p in pages)
            needs_ocr = self._needs_ocr(pages, document.source_type)
            force_ocr = (document.processing_metadata or {}).get("force_ocr", False)
            
            # Run preflight checks if OCR is needed
            preflight_result = None
            if needs_ocr or force_ocr:
                try:
                    preflight_result = OcrPreflight.check()
                    # Store preflight results in metadata
                    meta = dict(document.processing_metadata or {})
                    meta["ocr_preflight"] = {
                        "tesseract_found": preflight_result["tesseract_found"],
                        "tesseract_path": preflight_result["tesseract_path"],
                        "poppler_found": preflight_result["poppler_found"],
                        "poppler_path": preflight_result["poppler_path"],
                    }
                    document.processing_metadata = meta
                    self.db.commit()
                    
                    # QA logging: Log when chars=0 triggers OCR (after preflight)
                    if total_chars == 0:
                        logger.info(
                            "ocr_triggered_zero_chars",
                            extra={
                                "document_id": str(document_id),
                                "total_chars": 0,
                                "needs_ocr": needs_ocr,
                                "force_ocr": force_ocr,
                                "pdf_type": (document.processing_metadata or {}).get("pdf_type", "unknown"),
                                "preflight_result": {
                                    "tesseract_found": preflight_result["tesseract_found"],
                                    "poppler_found": preflight_result["poppler_found"],
                                },
                            },
                        )
                    
                    # If OCR is required but binaries are missing, fail with actionable error
                    if (needs_ocr or force_ocr) and preflight_result["errors"]:
                        error_msg = "\n".join(preflight_result["errors"])
                        raise OcrPreflightError(error_msg)
                except OcrPreflightError:
                    raise  # Re-raise preflight errors as-is
                except Exception as e:
                    logger.warning(f"Preflight check failed: {e}, continuing with provider validation")
            
            ocr_provider_ok = self.ocr_provider.validate_config()
            if needs_ocr and not ocr_provider_ok:
                raise RuntimeError(
                    f"OCR required for document {document_id} (scanned/low-text PDF or image) but OCR provider is not available. "
                    "Install Tesseract and Poppler: Windows https://github.com/UB-Mannheim/tesseract/wiki, "
                    "Linux: sudo apt-get install tesseract-ocr poppler-utils. "
                    "Do not silently continue with empty or low-quality text."
                )
            ocr_attempted = False
            total_chars_before_ocr = total_chars  # Store before OCR
            if (needs_ocr or force_ocr) and ocr_provider_ok:
                ocr_attempted = True
                t0 = time.perf_counter()
                await self._update_status(document_id, DocumentStatus.OCR_RUNNING.value, processing_run)
                try:
                    # Run OCR in batches so we don't hold all page images in memory
                    # and so we can persist progress incrementally (avoids "stuck at 0 pages").
                    batch_size = int(os.getenv("OCR_BATCH_SIZE") or 10)
                    dpi = int(os.getenv("OCR_DPI") or 300)
                    thread_count = os.getenv("OCR_THREAD_COUNT")

                    total_pages = len(pages) if pages else (document.total_pages or 0)
                    if total_pages <= 0:
                        # Fallback: if we cannot infer pages, run OCR in one pass
                        pages = await self._run_ocr(document, pages)
                        total_pages = len(pages)
                    else:
                        ocr_pages: List[Any] = []
                        for start_page in range(1, total_pages + 1, batch_size):
                            end_page = min(total_pages, start_page + batch_size - 1)
                            logger.info(
                                "ocr_batch_start",
                                extra={
                                    "document_id": str(document_id),
                                    "start_page": start_page,
                                    "end_page": end_page,
                                    "dpi": dpi,
                                    "batch_size": batch_size,
                                },
                            )
                            batch = await self.ocr_provider.run_ocr(
                                document.file_path,
                                language="eng",
                                first_page=start_page,
                                last_page=end_page,
                                dpi=dpi,
                                thread_count=thread_count,
                            )
                            # Update page_texts for this batch and commit immediately
                            for page in batch:
                                page_text = self.db.query(PageText).filter(
                                    PageText.document_id == document_id,
                                    PageText.page_no == page.page_no
                                ).first()
                                if page_text:
                                    page_text.text = page.text
                                    page_text.char_count = page.char_count
                                    page_text.ocr_confidence = page.ocr_confidence
                                    page_text.ocr_engine = page.ocr_engine
                            ocr_pages.extend(batch)
                            processing_run.pages_processed = min(end_page, total_pages)
                            self.db.commit()
                            logger.info(
                                "ocr_batch_complete",
                                extra={
                                    "document_id": str(document_id),
                                    "start_page": start_page,
                                    "end_page": end_page,
                                    "pages_processed": processing_run.pages_processed,
                                    "total_pages": total_pages,
                                },
                            )

                        pages = ocr_pages

                    duration_ms = int((time.perf_counter() - t0) * 1000)
                    logger.info(
                        "step_complete",
                        extra={"document_id": str(document_id), "step": "ocr_running", "duration_ms": duration_ms, "pages": len(pages), "provider": getattr(self.ocr_provider, "provider_name", "unknown")},
                    )
                    # Recalculate total chars after OCR
                    total_chars = sum(p.char_count for p in pages)
                    logger.info(
                        "ocr_complete",
                        extra={
                            "document_id": str(document_id),
                            "total_chars_before_ocr": total_chars_before_ocr,
                            "total_chars_after_ocr": total_chars,
                            "preflight_result": preflight_result,
                            "ocr_attempted": True,
                        },
                    )
                except Exception as ocr_error:
                    logger.error(f"OCR failed for document {document_id}: {ocr_error}", exc_info=True)
                    raise RuntimeError(
                        f"OCR failed: {ocr_error}. Install Tesseract and Poppler (pdf2image). "
                        "Fail loudly; do not continue with empty pages."
                    ) from ocr_error
            
            # MIN_CHARS_EXTRACT checkpoint: Run AFTER OCR attempt
            # This ensures OCR has a chance to extract text before we fail
            total_chars = sum(p.char_count for p in pages)
            min_chars = getattr(settings, "MIN_CHARS_EXTRACT", 1)
            if total_chars < min_chars:
                meta = dict(document.processing_metadata or {})
                pdf_type = meta.get("pdf_type", "unknown")
                raise ValueError(
                    f"Extraction checkpoint failed: total chars {total_chars} < MIN_CHARS_EXTRACT ({min_chars}). "
                    f"extractor used, pdf_type={pdf_type}, OCR attempted={'yes' if ocr_attempted else 'no'}"
                )
            
            # Step 3: Normalize
            await self._update_status(document_id, DocumentStatus.NORMALIZING.value, processing_run)
            normalized_pages = self._normalize_text(pages)
            # Math: density + extraction + markers
            math_density_per_page = [compute_math_density(p.text) for p in normalized_pages]
            math_density_doc = sum(math_density_per_page) / len(math_density_per_page) if normalized_pages else 0.0
            meta = dict(document.processing_metadata or {})
            meta["math_density"] = math_density_doc
            meta["content_type_hint"] = "math" if math_density_doc >= MATH_DENSITY_THRESHOLD else None
            document.processing_metadata = meta
            self.db.commit()
            if self.math_provider.validate_config():
                math_blocks = self.math_provider.extract_math(str(document_id), normalized_pages)
                from app.domains.content_ingestion.models import MathBlock as MathBlockModel
                for mb in math_blocks:
                    self.db.add(MathBlockModel(
                        document_id=document_id,
                        page_no=mb.page_no,
                        block_type=mb.block_type,
                        raw_text=mb.raw_text,
                        normalized_text=mb.normalized_text,
                        bbox_json=mb.bbox_json,
                        confidence=float(mb.confidence) if mb.confidence is not None else None,
                        provider_name=mb.provider_name,
                    ))
                self.db.commit()
                normalized_pages = [BaselineMathExtractionProvider.inject_markers_into_text(p) for p in normalized_pages]
            
            # Step 4: Chunking
            t0 = time.perf_counter()
            await self._update_status(document_id, DocumentStatus.CHUNKING.value, processing_run)
            chunks = self.chunker.chunk(
                normalized_pages,
                chunk_size_tokens=settings.CHUNK_SIZE_TOKENS,
                overlap_tokens=settings.CHUNK_OVERLAP_TOKENS,
                chapter_map=document.chapter_map
            )
            duration_ms = int((time.perf_counter() - t0) * 1000)
            logger.info(
                "step_complete",
                extra={"document_id": str(document_id), "step": "chunking", "duration_ms": duration_ms, "chunks": len(chunks) if chunks else 0, "pages": len(normalized_pages)},
            )
            if not chunks:
                non_empty = sum(1 for p in normalized_pages if (p.text or "").strip())
                sample = (normalized_pages[0].text[:200] if normalized_pages and normalized_pages[0].text else "")
                raise ValueError(
                    f"Chunking checkpoint failed: chunks=0. pages={len(normalized_pages)}, non_empty_pages={non_empty}, sample_snippet={sample!r}"
                )
            processing_run.chunks_created = len(chunks)
            self.db.commit()

            # Before embedding: filter empty chunks
            chunks = [c for c in chunks if (c.text or "").strip()]
            removed = processing_run.chunks_created - len(chunks)
            if removed:
                logger.warning(f"Filtered {removed} empty chunks", extra={"document_id": str(document_id)})
            if not chunks:
                raise ValueError("All chunks were empty after filtering; cannot embed.")
            
            # Step 5: Embedding
            t0 = time.perf_counter()
            await self._update_status(document_id, DocumentStatus.EMBEDDING.value, processing_run)
            chunk_texts = [chunk.text for chunk in chunks]
            embeddings = await self.embedding_provider.embed(chunk_texts)
            duration_ms = int((time.perf_counter() - t0) * 1000)
            logger.info(
                "step_complete",
                extra={"document_id": str(document_id), "step": "embedding", "duration_ms": duration_ms, "count": len(embeddings), "provider": self.embedding_provider.provider_name},
            )
            
            if len(embeddings) != len(chunks):
                raise ValueError(f"Embedding count mismatch: {len(embeddings)} != {len(chunks)}")
            
            # Step 6: Indexing (store in vector DB)
            await self._update_status(document_id, DocumentStatus.INDEXING.value, processing_run)
            stored_count = await self.vector_store.upsert(
                chunks=chunks,
                vectors=embeddings,
                document_id=str(document_id),
                pack_id=str(document.pack_id),
                embedding_model=getattr(self.embedding_provider, "embedding_model", None) or self.embedding_provider.provider_name,
                embedding_dim=self.embedding_provider.get_embedding_dimension(),
                embedding_provider=self.embedding_provider.provider_name,
            )
            
            processing_run.vectors_stored = stored_count
            processing_run.progress_percentage = 90
            self.db.commit()
            
            # Step 7: QA Validation
            await self._update_status(document_id, DocumentStatus.QA_VALIDATION.value, processing_run)
            from app.domains.content_ingestion.services.qa_service import QAService
            qa_service = QAService(self.db)
            qa_validation = qa_service.run_qa_validation(document_id)
            
            # Step 8: Verify chunks and embeddings were saved (embedding_v for fake/local)
            from app.domains.content_ingestion.models import Chunk
            active_provider = self.embedding_provider.provider_name
            if active_provider in ("fake", "local"):
                chunks_with_embeddings = self.db.query(Chunk).filter(
                    Chunk.document_id == document_id,
                    Chunk.embedding_v.isnot(None),
                    Chunk.embedding_model == active_provider
                ).count()
            else:
                chunks_with_embeddings = self.db.query(Chunk).filter(
                    Chunk.document_id == document_id,
                    Chunk.embedding.isnot(None)
                ).count()
            
            if chunks_with_embeddings == 0:
                error_msg = f"No chunks with embeddings found. Expected chunks but found 0. Document cannot be published."
                logger.error(f"Document {document_id} processing failed: {error_msg}")
                await self._update_status(
                    document_id,
                    DocumentStatus.FAILED.value,
                    processing_run,
                    error_code="NO_CHUNKS_SAVED",
                    error_message=error_msg,
                    remediation_hint="Document processing completed but no chunks were saved. Check embedding provider configuration and retry."
                )
                raise ValueError(error_msg)
            
            logger.info(f"Document {document_id} has {chunks_with_embeddings} chunks with embeddings saved")
            
            # Step 9: QA Validation
            await self._update_status(document_id, DocumentStatus.QA_VALIDATION.value, processing_run)
            from app.domains.content_ingestion.services.qa_service import QAService
            qa_service = QAService(self.db)
            qa_validation = qa_service.run_qa_validation(document_id)
            
            # Step 10: Publish (only if chunks and embeddings are saved)
            if qa_validation.qa_status == "passed":
                logger.info(f"Document {document_id} passed QA validation")
            else:
                logger.warning(f"Document {document_id} did not pass QA validation, but publishing anyway")
                logger.warning(f"QA checks: page_coverage={qa_validation.page_coverage_check}, "
                             f"text_density={qa_validation.text_density_check}, "
                             f"embedding_completeness={qa_validation.embedding_completeness_check}, "
                             f"vector_retrieval={qa_validation.vector_retrieval_check}")
            
            # Verify again before publishing (embedding_v for fake/local)
            if active_provider in ("fake", "local"):
                final_chunk_count = self.db.query(Chunk).filter(
                    Chunk.document_id == document_id,
                    Chunk.embedding_v.isnot(None),
                    Chunk.embedding_model == active_provider
                ).count()
            else:
                final_chunk_count = self.db.query(Chunk).filter(
                    Chunk.document_id == document_id,
                    Chunk.embedding.isnot(None)
                ).count()
            
            if final_chunk_count == 0:
                error_msg = f"Chunks verification failed before publishing. Found 0 chunks with embeddings."
                logger.error(f"Document {document_id} cannot be published: {error_msg}")
                await self._update_status(
                    document_id,
                    DocumentStatus.FAILED.value,
                    processing_run,
                    error_code="CHUNKS_VERIFICATION_FAILED",
                    error_message=error_msg,
                    remediation_hint="Chunks were not properly saved. Check vector store configuration and retry."
                )
                raise ValueError(error_msg)
            
            # Publish only if chunks are verified
            await self._update_status(document_id, DocumentStatus.PUBLISHED.value, processing_run)
            document.processed_at = processing_run.completed_at
            processing_run.status = DocumentStatus.PUBLISHED.value
            processing_run.progress_percentage = 100
            logger.info(f"Document {document_id} published successfully with {final_chunk_count} chunks (QA status: {qa_validation.qa_status})")
            
            from datetime import datetime, timezone
            processing_run.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            
            return document
            
        except Exception as e:
            logger.error(f"Ingestion failed for document {document_id}: {e}", exc_info=True)
            
            # Provide more detailed error messages based on error type
            error_str = str(e)
            error_code = "INGESTION_ERROR"
            remediation_hint = "Check logs and retry document processing"
            # Persist failure context (additive, no API changes)
            try:
                document = self.db.query(Document).filter(Document.id == document_id).first()
                if document:
                    meta = dict(document.processing_metadata or {})
                    meta["failed_step"] = processing_run.current_step
                    meta["error_code"] = error_code
                    meta["provider_context"] = {
                        "ocr": getattr(self.ocr_provider, "provider_name", None),
                        "embedding": getattr(self.embedding_provider, "provider_name", None),
                        "vector_store": getattr(self.vector_store, "provider_name", None),
                        "chunker": getattr(self.chunker, "provider_name", None),
                    }
                    document.processing_metadata = meta
                    self.db.commit()
            except Exception:
                pass
            
            if isinstance(e, OcrPreflightError):
                error_code = "OCR_ERROR"
                remediation_hint = error_str  # Preflight error already contains actionable instructions
            elif "OPENAI_API_KEY" in error_str or "api key" in error_str.lower() or "authentication" in error_str.lower():
                error_code = "MISSING_API_KEY"
                remediation_hint = "Set OPENAI_API_KEY in your .env file and restart the backend."
            elif "tesseract" in error_str.lower() or "ocr" in error_str.lower() or "TesseractNotFoundError" in error_str:
                error_code = "OCR_ERROR"
                remediation_hint = "Install Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki (Windows) or 'sudo apt-get install tesseract-ocr' (Linux)"
            elif "file not found" in error_str.lower() or "FileNotFoundError" in error_str:
                error_code = "FILE_NOT_FOUND"
                remediation_hint = "The uploaded file may have been deleted or moved. Try re-uploading the document."
            elif "embedding" in error_str.lower() or "Embedding" in error_str:
                error_code = "EMBEDDING_ERROR"
                remediation_hint = "Check OPENAI_API_KEY, network connectivity, and OpenAI service status."
            elif "vector" in error_str.lower() or "pgvector" in error_str.lower() or "database" in error_str.lower():
                error_code = "VECTOR_STORE_ERROR"
                remediation_hint = "Check database connection, ensure pgvector extension is enabled, and verify database permissions."
            elif "No text extracted" in error_str or "empty" in error_str.lower():
                error_code = "TEXT_EXTRACTION_ERROR"
                remediation_hint = "The document may be corrupted, password-protected, or in an unsupported format. Try a different document or enable OCR."
            
            await self._update_status(
                document_id,
                DocumentStatus.FAILED.value,
                processing_run,
                error_code=error_code,
                error_message=error_str,
                remediation_hint=remediation_hint
            )
            raise

    async def reprocess_document(self, document_id: UUID, start_step: str = "text_extracting") -> Document:
        """
        Internal reprocessing entrypoint (no endpoint changes).
        Currently re-runs full pipeline; start_step is stored for audit/future resuming.
        """
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")
        meta = dict(document.processing_metadata or {})
        meta["reprocess_from_step"] = start_step
        meta["reprocess_embedding_provider"] = getattr(self.embedding_provider, "provider_name", None)
        meta["reprocess_ocr_provider"] = getattr(self.ocr_provider, "provider_name", None)
        document.processing_metadata = meta
        self.db.commit()
        return await self.ingest_document(document_id)
    
    async def _extract_text(self, document: Document) -> List:
        """Extract text from document based on source type."""
        file_path = document.file_path
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document file not found: {file_path}")
        
        if document.source_type == "pdf":
            return await self.pdf_extractor.extract_text(file_path)
        elif document.source_type == "docx":
            return await self.docx_extractor.extract_text(file_path)
        else:
            raise ValueError(f"Unsupported source type: {document.source_type}")
    
    def _needs_ocr(self, pages: List, source_type: str) -> bool:
        """Determine if OCR is needed based on text density."""
        if source_type != "pdf":
            return False
        
        if not pages:
            return True
        
        # Check total chars first - if 0, OCR is required regardless of pdf_type heuristic
        total_chars = sum(p.char_count for p in pages)
        if total_chars == 0:
            return True
        
        # Check average chars per page - if below threshold, needs OCR
        avg_chars = total_chars / len(pages) if pages else 0
        if avg_chars < settings.SCANNED_THRESHOLD_CHARS:
            return True
        
        return False
    
    async def _run_ocr(self, document: Document, pages: List) -> List:
        """Run OCR on document."""
        if not self.ocr_provider.validate_config():
            raise RuntimeError(f"OCR provider {settings.OCR_ENGINE} not properly configured")
        
        return await self.ocr_provider.run_ocr(document.file_path)
    
    def _normalize_text(self, pages: List) -> List:
        """Normalize extracted text."""
        # Simple normalization: clean whitespace, remove extra newlines
        from app.domains.content_ingestion.providers.base import PageText as PageTextBase
        normalized = []
        for page in pages:
            # Clean text
            text = page.text
            # Remove excessive whitespace
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            normalized_text = "\n".join(lines)
            
            # Create new PageText with normalized text
            normalized.append(PageTextBase(
                page_no=page.page_no,
                text=normalized_text,
                char_count=len(normalized_text),
                ocr_confidence=page.ocr_confidence,
                ocr_engine=page.ocr_engine
            ))
        
        return normalized
    
    async def _update_status(
        self,
        document_id: UUID,
        status: str,
        processing_run: DocumentProcessingRun,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        remediation_hint: Optional[str] = None
    ):
        """Update document and processing run status."""
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.status = status
            if error_code:
                document.error_code = error_code
            if error_message:
                document.error_message = error_message
            if remediation_hint:
                document.remediation_hint = remediation_hint
        
        processing_run.status = status
        processing_run.current_step = status
        if error_code:
            processing_run.error_code = error_code
        if error_message:
            processing_run.error_message = error_message
        if remediation_hint:
            processing_run.remediation_hint = remediation_hint
        
        # Update progress percentage based on status
        status_progress = {
            DocumentStatus.TEXT_EXTRACTING.value: 10,
            DocumentStatus.OCR_RUNNING.value: 20,
            DocumentStatus.NORMALIZING.value: 30,
            DocumentStatus.CHUNKING.value: 40,
            DocumentStatus.EMBEDDING.value: 60,
            DocumentStatus.INDEXING.value: 80,
            DocumentStatus.QA_VALIDATION.value: 90,
            DocumentStatus.PUBLISHED.value: 100,
            DocumentStatus.FAILED.value: 0,
        }
        processing_run.progress_percentage = status_progress.get(status, 0)
        
        self.db.commit()
        logger.info(f"Updated document {document_id} status to {status}")
