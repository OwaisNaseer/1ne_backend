"""
Worksheet generation service using RAG.
"""
import hashlib
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
from collections import defaultdict

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.domains.content_ingestion.models import WorksheetCache, ContentPack
from app.domains.content_ingestion.providers.vector_stores import PgVectorStore
from app.domains.content_ingestion.providers.embedding_providers import (
    OpenAIEmbeddingProvider,
    FakeEmbeddingProvider,
    LocalSentenceTransformersEmbeddingProvider,
)
from app.domains.content_ingestion.providers.base import VectorHit
from app.domains.content_ingestion.models import Chunk, Document
from app.llm.router import ModelRouter
from app.llm.config import llm_settings

logger = get_logger(__name__)


class WorksheetService:
    """Service for generating worksheets using RAG."""
    
    def __init__(self, db: Session):
        """Initialize worksheet service."""
        self.db = db
        self.vector_store = PgVectorStore(db=db)
        # Embedding provider will be determined dynamically based on pack's stored embeddings
        self.llm_router = ModelRouter(config=llm_settings)
    
    def _detect_pack_embedding_provider(self, pack_id: UUID) -> tuple[Any, str]:
        """
        Detect which embedding provider/model was used for chunks in this pack.
        Returns (embedding_provider_instance, embedding_model_string).
        """
        # Find a chunk from this pack to detect embedding provider
        chunk = self.db.query(Chunk).join(Document).filter(
            Document.pack_id == pack_id,
            Document.status == "published",
            Chunk.embedding_v.isnot(None)
        ).first()
        
        if not chunk:
            # Fallback to OpenAI if no chunks found
            logger.warning(f"No chunks found for pack {pack_id}, defaulting to OpenAI embeddings")
            return OpenAIEmbeddingProvider(), "openai"
        
        provider_name = chunk.embedding_provider or "fake"
        embedding_model = chunk.embedding_model or provider_name
        
        # Instantiate the correct provider
        if provider_name == "openai":
            return OpenAIEmbeddingProvider(), embedding_model
        elif provider_name == "local":
            return LocalSentenceTransformersEmbeddingProvider(), embedding_model
        else:
            # Default to fake for free mode
            return FakeEmbeddingProvider(), embedding_model
    
    # Pages 1..N are typically cover, TOC, copyright. Chunks from these are excluded for worksheet context.
    FRONT_MATTER_MAX_PAGE = 8

    async def generate_worksheet(
        self,
        pack_id: UUID,
        topic_id: Optional[str] = None,
        topic_text: Optional[str] = None,
        grade: Optional[str] = None,
        subject: Optional[str] = None,
        difficulty_mix: Optional[Dict[str, float]] = None,
        num_questions: int = 10,
        question_types: Optional[List[str]] = None,
        force_regenerate: bool = False,
    ) -> WorksheetCache:
        """
        Generate a worksheet using RAG.
        
        Args:
            pack_id: Content pack UUID
            topic_id: Optional topic ID from chapter map
            topic_text: Optional topic text (alternative to topic_id)
            grade: Grade level
            subject: Subject
            difficulty_mix: Difficulty distribution
            num_questions: Number of questions
            question_types: List of question types
            
        Returns:
            WorksheetCache object
        """
        # Check cache first (skip if force_regenerate)
        signature_hash = self._generate_signature_hash(
            pack_id, topic_id, topic_text, grade, subject, difficulty_mix, num_questions
        )
        
        if not force_regenerate:
            cached = self.db.query(WorksheetCache).filter(
                WorksheetCache.signature_hash == signature_hash
            ).first()
            if cached:
                logger.info(f"Returning cached worksheet: {cached.id}")
                return cached
        else:
            # Remove existing cache so we can insert the new worksheet (avoids 409 on unique signature_hash)
            self.db.query(WorksheetCache).filter(
                WorksheetCache.signature_hash == signature_hash
            ).delete()
            self.db.commit()
        
        # Generate new worksheet
        logger.info(f"Generating worksheet for pack {pack_id}, topic: {topic_text or topic_id}")
        
        # Normalize topic and expand query terms for retrieval (typo correction + synonyms)
        normalized_topic_text = self._normalize_topic_for_keywords(topic_text or "")
        expanded_query_terms = self._expand_query_synonyms(topic_text or "")
        base_query = topic_text or f"topic {topic_id}" if topic_id else "curriculum content"
        # Use expanded terms for vector search so we hit correct chapter (e.g. algebraic expression -> variable, coefficient, simplify)
        query_text = " ".join(expanded_query_terms[:20]) + " chapter section explanation examples" if expanded_query_terms else f"{base_query} chapter section explanation examples"
        
        # Detect which embedding provider was used for this pack
        embedding_provider, embedding_model = self._detect_pack_embedding_provider(pack_id)
        logger.info(f"Using embedding provider: {embedding_provider.provider_name}, model: {embedding_model}")
        
        skip_pages = self.FRONT_MATTER_MAX_PAGE
        top_k = min(20, num_questions * 3)
        context_min_chunks = 6
        context_max_chunks = 10
        relevance_sim_threshold = 0.32
        relevance_keyword_min = 2
        page_window_size = 4  # 4-page bins for cluster-by-page
        stage_a_top_k = 80
        max_chapter_ranges = 3
        high_sim_cutoff = 0.35  # chunk passes "keyword or high sim" if sim >= this

        # Stage A: cluster-by-page — top 80 hits, 4-page bins, densest high-similarity cluster(s)
        hits_broad: List[VectorHit] = []
        if embedding_provider.provider_name != "fake":
            try:
                query_embeddings = await embedding_provider.embed([query_text])
                if query_embeddings and len(query_embeddings) > 0:
                    hits_broad = await self.vector_store.query(
                        query_vector=query_embeddings[0],
                        pack_id=str(pack_id),
                        top_k=stage_a_top_k,
                        topic_id=topic_id,
                        embedding_model=embedding_model,
                    )
            except Exception as e:
                logger.warning(f"Vector search failed: {e}, falling back to text search")
        if not hits_broad:
            hits_broad = self._text_based_search(
                pack_id=pack_id, query_text=query_text, topic_id=topic_id, top_k=stage_a_top_k
            )
        hits_after_front = [h for h in hits_broad if (h.metadata or {}).get("page_start_pdf", 0) > skip_pages]
        if not hits_after_front:
            any_have_page = any((h.metadata or {}).get("page_start_pdf") is not None for h in hits_broad)
            if hits_broad and any_have_page:
                raise ValueError(
                    "Topic content not found in this book pack. All retrieved content is from early pages (cover/TOC). Try another topic."
                )
            hits_after_front = hits_broad[:stage_a_top_k]
        keywords_topic = self._extract_topic_keywords(topic_text or "")
        # Cluster by 4-page bins; score = density (count) + avg similarity + keyword bonus
        window_scores: Dict[Tuple[int, int], Tuple[float, int, float]] = defaultdict(lambda: (0.0, 0, 0.0))  # total_sim, count, keyword_bonus
        for h in hits_after_front:
            p = (h.metadata or {}).get("page_start_pdf")
            if p is None:
                continue
            window_start = ((p - 1) // page_window_size) * page_window_size + 1
            window_end = window_start + page_window_size - 1
            key = (window_start, window_end)
            sim = getattr(h, "similarity_score", 0)
            prev_sim, prev_count, prev_kw = window_scores[key]
            kw_bonus = 0.1 if any(kw in (h.text or "").lower() for kw in keywords_topic) else 0.0
            window_scores[key] = (prev_sim + sim, prev_count + 1, prev_kw + kw_bonus)
        scored_ranges: List[Tuple[Tuple[int, int], float]] = []
        for (lo, hi), (total_sim, count, kw_bonus) in window_scores.items():
            if count == 0:
                continue
            avg_sim = total_sim / count
            score = avg_sim + 0.05 * min(count, 8) + kw_bonus
            scored_ranges.append(((lo, hi), score))
        scored_ranges.sort(key=lambda x: -x[1])
        top5_ranges_for_debug = [(r[0], r[1]) for r in scored_ranges[:5]]
        chosen_ranges = [r[0] for r in scored_ranges[:max_chapter_ranges]]
        if not chosen_ranges:
            min_page_range = 0
            max_page_range = 99999
            chosen_ranges = [(0, 99999)]
        else:
            min_page_range = min(r[0] for r in chosen_ranges)
            max_page_range = max(r[1] for r in chosen_ranges)
        logger.info(f"Worksheet Stage A: chosen chapter page ranges {chosen_ranges} (using {min_page_range}-{max_page_range}), top5 scores={[(r, round(s,3)) for r,s in top5_ranges_for_debug]}")

        # Stage B: retrieve within best cluster range (more candidates, then filter to 6-10)
        hits: List[VectorHit] = []
        for attempt in range(2):
            if embedding_provider.provider_name != "fake":
                try:
                    query_embeddings = await embedding_provider.embed([query_text])
                    if query_embeddings and len(query_embeddings) > 0:
                        hits = await self.vector_store.query(
                            query_vector=query_embeddings[0],
                            pack_id=str(pack_id),
                            top_k=25,
                            topic_id=topic_id,
                            embedding_model=embedding_model,
                            filters={"min_page": min_page_range - 1, "max_page": max_page_range},
                        )
                except Exception as e:
                    logger.warning(f"Stage B vector search failed: {e}")
            if not hits:
                hits = [h for h in hits_after_front if (h.metadata or {}).get("page_start_pdf") is not None and min_page_range <= (h.metadata or {}).get("page_start_pdf", 0) <= max_page_range][:25]
            if hits:
                break
            if attempt == 0 and len(chosen_ranges) < 3 and len(scored_ranges) >= 3:
                min_page_range = min(r[0] for r in scored_ranges[:3])
                max_page_range = max(r[1] for r in scored_ranges[:3])
                continue
            break
        if not hits:
            self._raise_topic_not_found(
                top5_ranges_for_debug, chosen_ranges, hits_after_front, topic_text or "", None, 0.0, 0
            )
        # Tighten: only 6-10 chunks with topic keyword hit OR high similarity
        keywords_topic_list = self._extract_topic_keywords(topic_text or "")
        def chunk_relevance(h: VectorHit) -> Tuple[float, int]:
            sim = getattr(h, "similarity_score", 0)
            text_lower = (h.text or "").lower()
            kw_hits = sum(1 for kw in keywords_topic_list if kw in text_lower)
            return (sim + 0.1 * min(kw_hits, 3), kw_hits)
        filtered = [h for h in hits if chunk_relevance(h)[1] >= 1 or getattr(h, "similarity_score", 0) >= high_sim_cutoff]
        if not filtered:
            filtered = hits
        filtered.sort(key=lambda h: -chunk_relevance(h)[0])
        hits = filtered[:context_max_chunks]
        if len(hits) < context_min_chunks and len(filtered) >= context_min_chunks:
            hits = filtered[:context_min_chunks]
        avg_sim, keyword_hits = self._relevance_score(hits, topic_text or "")
        logger.info(f"Worksheet Stage B: {len(hits)} chunks (6-10), relevance avg_sim={avg_sim:.3f}, keyword_hits={keyword_hits}")
        if avg_sim < relevance_sim_threshold or keyword_hits < relevance_keyword_min:
            if len(chosen_ranges) < 3 and len(scored_ranges) >= 3:
                min_page_range = min(r[0] for r in scored_ranges[:3])
                max_page_range = max(r[1] for r in scored_ranges[:3])
                hits = [h for h in hits_after_front if (h.metadata or {}).get("page_start_pdf") is not None and min_page_range <= (h.metadata or {}).get("page_start_pdf", 0) <= max_page_range]
                filtered = [h for h in hits if chunk_relevance(h)[1] >= 1 or getattr(h, "similarity_score", 0) >= high_sim_cutoff]
                if not filtered:
                    filtered = hits
                filtered.sort(key=lambda h: -chunk_relevance(h)[0])
                hits = filtered[:context_max_chunks]
                if hits:
                    avg_sim, keyword_hits = self._relevance_score(hits, topic_text or "")
            if avg_sim < relevance_sim_threshold or keyword_hits < relevance_keyword_min:
                self._raise_topic_not_found(top5_ranges_for_debug, chosen_ranges, hits_after_front, topic_text or "", hits, avg_sim, keyword_hits)
        for i, h in enumerate(hits[:5]):
            meta = h.metadata or {}
            logger.info(
                f"Worksheet chunk[{i}] id={h.chunk_id} page_start_pdf={meta.get('page_start_pdf')} "
                f"page_end_pdf={meta.get('page_end_pdf')} score={getattr(h, 'similarity_score', None)}"
            )

        # Build context with metadata (chunk_id, document_id, page_range) so LLM can cite (hits already 6-10)
        context_parts = []
        for hit in hits:
            meta = hit.metadata or {}
            start = meta.get("page_start_pdf")
            end = meta.get("page_end_pdf")
            if start is not None and end is not None:
                page_range = f"{start}-{end}"
            elif start is not None:
                page_range = str(start)
            elif end is not None:
                page_range = str(end)
            else:
                page_range = ""
            context_parts.append(
                f"[chunk_id: {hit.chunk_id}, document_id: {hit.document_id}, page_range: {page_range}]\n{hit.text}"
            )
        context_with_metadata = "\n\n---\n\n".join(context_parts)
        context_chunks = [hit.text for hit in hits]
        context_text_flat = " ".join(context_chunks)
        allowed_concepts, forbidden_concepts = self._build_allowed_forbidden(context_text_flat, topic_text or "")
        logger.info(f"Worksheet prompt: allowed_concepts={allowed_concepts[:8]}, forbidden_concepts={forbidden_concepts[:8]}")

        # MCQ vs short count from question_types (e.g. ["mcq", "short_answer"] -> half each)
        question_types_resolved = question_types or ["mcq", "short_answer"]
        wants_mcq = any((t or "").lower() in ("mcq", "multiple_choice") for t in question_types_resolved)
        wants_short = any((t or "").lower() in ("short_answer", "short") for t in question_types_resolved)
        if wants_mcq and wants_short:
            mcq_count = num_questions // 2
            short_count = num_questions - mcq_count
        elif wants_mcq:
            mcq_count = num_questions
            short_count = 0
        else:
            mcq_count = 0
            short_count = num_questions

        # Generate worksheet using LLM; retry once if question count short or topic validation fails
        worksheet_json = None
        context_for_retry = context_with_metadata
        hits_for_retry = hits
        for attempt in range(2):
            try:
                worksheet_json = await self._generate_worksheet_with_llm(
                    context_with_metadata=context_for_retry,
                    pack_id=str(pack_id),
                    topic_text=topic_text or f"Topic {topic_id}",
                    normalized_topic_text=normalized_topic_text,
                    grade=grade or "",
                    subject=subject or "",
                    num_questions=num_questions,
                    mcq_count=mcq_count,
                    short_count=short_count,
                    allowed_concepts=allowed_concepts,
                    forbidden_concepts=forbidden_concepts,
                )
            except Exception as llm_error:
                logger.warning(f"LLM worksheet generation failed (attempt {attempt + 1}): {llm_error}", exc_info=True)
                if attempt == 1:
                    raise ValueError(
                        "Worksheet generation failed. Please try again or use a different topic. "
                        "If the error persists, check LLM/OpenAI configuration. Underlying error: " + str(llm_error)
                    ) from llm_error
                continue
            questions_list = (worksheet_json or {}).get("questions", [])
            if len(questions_list) < num_questions:
                if attempt == 0:
                    logger.warning(f"LLM returned {len(questions_list)} questions (required {num_questions}); retrying once")
                    continue
                raise ValueError(
                    f"Generator returned {len(questions_list)} questions; required at least {num_questions}."
                )
            valid, report = self._validate_questions_topic(questions_list, topic_text or "")
            if valid:
                break
            if attempt == 0:
                logger.warning(f"Topic validation failed: {report}; retrying with stricter prompt and top 6 chunks")
                context_for_retry = "\n\n---\n\n".join(
                    f"[chunk_id: {h.chunk_id}, document_id: {h.document_id}, page_range: {(h.metadata or {}).get('page_start_pdf', '')}-{(h.metadata or {}).get('page_end_pdf', '')}]\n{h.text}"
                    for h in hits_for_retry[:6]
                )
                allowed_concepts, forbidden_concepts = self._build_allowed_forbidden(" ".join(h.text for h in hits_for_retry[:6]), topic_text or "")
                continue
            self._log_validation_fail_debug(
                normalized_topic_text, expanded_query_terms, top5_ranges_for_debug,
                (min_page_range, max_page_range), hits_for_retry[:15]
            )
            raise ValueError("VALIDATION_FAILED: " + report)
        
        # Build citations list for API (chunk_id, document_id, page_range per hit)
        citations_list = []
        for hit in hits:
            meta = hit.metadata or {}
            start = meta.get("page_start_pdf")
            end = meta.get("page_end_pdf")
            if start is not None and end is not None:
                page_range = f"{start}-{end}"
            elif start is not None:
                page_range = str(start)
            elif end is not None:
                page_range = str(end)
            else:
                page_range = ""
            citations_list.append({
                "chunk_id": hit.chunk_id,
                "document_id": hit.document_id,
                "page_range": page_range,
            })

        # Create cache entry
        worksheet_cache = WorksheetCache(
            signature_hash=signature_hash,
            pack_id=pack_id,
            topic_id=topic_id,
            topic_text=topic_text,
            grade=grade,
            subject=subject,
            difficulty_mix=difficulty_mix,
            num_questions=num_questions,
            worksheet_json=worksheet_json,
            chunk_ids_used=[hit.chunk_id for hit in hits],
            retrieval_metadata={
                "query": query_text,
                "top_k": top_k,
                "similarity_scores": [hit.similarity_score for hit in hits],
                "citations": citations_list,
                "chapter_page_range": f"{min_page_range}-{max_page_range}",
                "relevance_avg_sim": avg_sim,
                "relevance_keyword_hits": keyword_hits,
            }
        )
        
        self.db.add(worksheet_cache)
        self.db.commit()
        self.db.refresh(worksheet_cache)
        
        logger.info(f"Generated worksheet: {worksheet_cache.id}")
        return worksheet_cache
    
    async def _generate_worksheet_with_llm(
        self,
        context_with_metadata: str,
        pack_id: str,
        topic_text: str,
        grade: str,
        subject: str,
        num_questions: int,
        mcq_count: int,
        short_count: int,
        allowed_concepts: Optional[List[str]] = None,
        forbidden_concepts: Optional[List[str]] = None,
        normalized_topic_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate worksheet JSON using LLM with international-standard assessment prompt."""
        allowed = (allowed_concepts or [])[:15]
        forbidden = (forbidden_concepts or [])[:12]
        norm = (normalized_topic_text or topic_text or "").lower()
        is_algebraic = "algebra" in norm or "expression" in norm
        algebraic_rules = ""
        if is_algebraic:
            algebraic_rules = """
ALGEBRAIC EXPRESSION TOPIC — STRICT REQUIREMENTS:
- At least 8 out of 10 questions MUST include variables (x, y, a, b) or expressions like 2x+3, 3y-1, coefficients, constants.
- Include exactly: 3 "simplify expression" questions, 2 "evaluate for given variable values", 2 "identify terms/coefficients/constants", 1 "translate words to expression"; remaining can be mixed algebraic.
- MCQ options MUST be algebraic expressions (e.g. 2x+5, 3a-2), NOT number theory (no HCF, LCM, primes, integers).
- Do NOT write questions on prime numbers, factors, HCF, LCM, or integers unless the CONTEXT explicitly is about algebra.
"""

        system_message = f"""You are an international-standard assessment author and a strict JSON generator.

CRITICAL: You MUST generate questions strictly about the topic: "{topic_text}". Use ONLY the provided book excerpts. If excerpts do not contain the topic, do not invent content from other topics.

HARD RULES:
1) Output MUST be valid JSON only. No markdown, no explanations, no extra text.
2) Use ONLY the provided CONTEXT. Do not use outside knowledge.
3) Do NOT write "Based on the content/passage/context…" and do NOT ask to explain a paragraph.
4) Create real assessment items ONLY on the topic "{topic_text}":
   - MCQ: 4 options (A–D), exactly 1 correct, plausible distractors.
   - Short: concise answer (rule statement or computed result).
5) Return EXACTLY num_questions questions, numbered 1..num_questions.
6) Every question MUST include at least one citation: {{chunk_id, document_id, page_range}}.
7) Answers must NOT be copied verbatim from context. They must be short and student-facing.
8) Provide a professional marking scheme with mark allocation + acceptable answers + common errors.
9) Allowed concepts (use these from the excerpts): {", ".join(allowed) if allowed else "from context"}.
10) FORBIDDEN: Do NOT write questions about: {", ".join(forbidden) if forbidden else "unrelated topics"}.
{algebraic_rules}

Generate an international-level worksheet and marking scheme in JSON. Return ONLY the final JSON."""

        user_prompt = f"""INPUT:
{{
  "pack_id": "{pack_id}",
  "topic_text": "{topic_text}",
  "grade": "{grade}",
  "subject": "{subject}",
  "num_questions": {num_questions},
  "mix": {{ "mcq": {mcq_count}, "short": {short_count} }}
}}

CONTEXT (authoritative book excerpts — use only this; cite chunk_id, document_id, page_range in each question):
{context_with_metadata}

OUTPUT JSON SCHEMA (MUST match exactly). Return ONLY this JSON, no other text:
{{
  "questions": [
    {{
      "question_id": 1,
      "type": "mcq" or "short",
      "difficulty": "easy" or "medium" or "hard",
      "question_text": "<string>",
      "math_content": true or false,
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correct_option": "A" or "B" or "C" or "D",
      "answer_text": "<string>",
      "marks": 1 or 2 or 3,
      "citations": [{{"chunk_id": "<string>", "document_id": "<string>", "page_range": "<string>"}}]
    }}
  ],
  "answer_key": [{{"question_id": 1, "answer": "<string>"}}],
  "marking_scheme": [
    {{
      "question_id": 1,
      "total_marks": 1,
      "mark_allocation": [{{"criteria": "<string>", "marks": 1}}],
      "acceptable_answers": ["<string>"],
      "common_errors": ["<string>"]
    }}
  ]
}}

QUESTION RULES:
- Exactly {mcq_count} MCQ and exactly {short_count} short questions.
- Difficulty: ~20% easy, ~60% medium, ~20% hard.
- MCQ marks = 1. Short marks = 2 or 3.
- Every question must cite relevant chunks from CONTEXT. Use LaTeX for math: $formula$.
""" + (
    """
- ALGEBRAIC TOPIC: At least 8/10 questions must include variables (x, y, a, b) or expressions (2x+3, coefficients, terms). Include: 3 simplify expression, 2 evaluate for given values, 2 identify terms/coefficients/constants, 1 translate words to expression. MCQ options must be algebraic expressions, not number theory."""
    if is_algebraic else ""
) + "\n"

        try:
            response = await self.llm_router.generate(
                system_message=system_message,
                prompt=user_prompt,
                model_config={
                    "provider": "openai",
                    "model": "gpt-4o-mini",
                    "temperature": 0.3,
                    "max_tokens": 5000
                }
            )

            if not response or not hasattr(response, "content"):
                logger.error("LLM response is empty or missing content")
                raise RuntimeError("LLM returned empty response")

            content = response.content.strip() if response.content else ""
            if not content:
                logger.error("LLM response content is empty")
                raise RuntimeError("LLM returned empty content")

            logger.debug(f"LLM response (first 500 chars): {content[:500]}")

            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            raw = json.loads(content)
            if "questions" not in raw:
                raise ValueError("Generated worksheet missing 'questions' field")

            # Normalize to existing API format (id "q1", question, correct_answer, answer_key dict, marking_scheme dict)
            worksheet_data = self._normalize_worksheet_to_api_format(raw)
            return worksheet_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse worksheet JSON: {e}")
            logger.error(f"Response content: {content[:1000] if 'content' in locals() else 'N/A'}")
            if not content or len(content.strip()) == 0:
                raise RuntimeError(
                    "LLM returned empty response. Check OpenAI API configuration: "
                    "OPENAI_API_KEY and OPENAI_BASE_URL must be valid."
                )
            raise ValueError(f"Invalid JSON in LLM response: {str(e)}. Content: {content[:200]}")
        except Exception as e:
            logger.error(f"Worksheet generation failed: {e}", exc_info=True)
            error_msg = str(e)
            if "api.opeanai.com" in error_msg.lower() or "invalid api key" in error_msg.lower():
                error_msg += ". Check OPENAI_BASE_URL in .env (may have typo: 'opeanai' instead of 'openai')"
            raise RuntimeError(f"Worksheet generation failed: {error_msg}")

    def _normalize_worksheet_to_api_format(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Map LLM output to existing API format. Handles both new schema (question_id, question_text) and legacy (id, question)."""
        questions_raw = raw.get("questions", [])
        if not questions_raw:
            return {"questions": [], "answer_key": {}, "marking_scheme": {}}

        # Legacy format: questions have "id" (e.g. "q1") and "question" (text)
        first = questions_raw[0]
        is_legacy = "id" in first and "question" in first and "question_id" not in first
        if is_legacy:
            return {
                "questions": questions_raw,
                "answer_key": raw.get("answer_key", {}),
                "marking_scheme": raw.get("marking_scheme", {}),
            }

        questions_out = []
        answer_key_out: Dict[str, str] = {}
        marking_scheme_out: Dict[str, Dict[str, Any]] = {}

        for q in questions_raw:
            qid_num = q.get("question_id", len(questions_out) + 1)
            qid_str = f"q{qid_num}"
            q_type = (q.get("type") or "short").lower()
            if q_type not in ("mcq", "short"):
                q_type = "short"
            question_text = q.get("question_text") or q.get("question", "")
            correct_option = q.get("correct_option")
            answer_text = q.get("answer_text") or q.get("correct_answer", "")
            correct_answer = correct_option if q_type == "mcq" and correct_option else answer_text
            options = q.get("options") if q_type == "mcq" else None
            marks = q.get("marks") or q.get("points", 1)
            difficulty = q.get("difficulty") or "medium"
            math_content = bool(q.get("math_content", False))

            questions_out.append({
                "id": qid_str,
                "type": "mcq" if q_type == "mcq" else "short_answer",
                "question": question_text,
                "options": options,
                "correct_answer": correct_answer,
                "explanation": None,
                "points": marks,
                "difficulty": difficulty,
                "math_content": math_content,
            })
            answer_key_out[qid_str] = correct_answer

            ms_entry = None
            for m in raw.get("marking_scheme", []):
                if m.get("question_id") == qid_num:
                    ms_entry = m
                    break
            if ms_entry:
                total_marks = ms_entry.get("total_marks", marks)
                allocation = ms_entry.get("mark_allocation", [])
                criteria_parts = [a.get("criteria", "") for a in allocation if a.get("criteria")]
                acceptable = ms_entry.get("acceptable_answers", [])
                common = ms_entry.get("common_errors", [])
                if acceptable:
                    criteria_parts.append("Acceptable: " + "; ".join(acceptable[:3]))
                if common:
                    criteria_parts.append("Common errors: " + "; ".join(common[:2]))
                marking_scheme_out[qid_str] = {
                    "points": total_marks,
                    "criteria": " ".join(criteria_parts) if criteria_parts else "See mark allocation.",
                }
            else:
                marking_scheme_out[qid_str] = {"points": marks, "criteria": "Answer as per context."}

        return {
            "questions": questions_out,
            "answer_key": answer_key_out,
            "marking_scheme": marking_scheme_out,
        }
    
    def _generate_signature_hash(
        self,
        pack_id: UUID,
        topic_id: Optional[str],
        topic_text: Optional[str],
        grade: Optional[str],
        subject: Optional[str],
        difficulty_mix: Optional[Dict[str, float]],
        num_questions: int
    ) -> str:
        """Generate cache signature hash."""
        signature_data = {
            "pack_id": str(pack_id),
            "topic_id": topic_id or "",
            "topic_text": topic_text or "",
            "grade": grade or "",
            "subject": subject or "",
            "difficulty_mix": json.dumps(difficulty_mix, sort_keys=True) if difficulty_mix else "",
            "num_questions": num_questions,
            "format_version": "1.5"  # 2-stage retrieval, topic relevance gate, prompt contract, post-validation
        }
        
        signature_str = json.dumps(signature_data, sort_keys=True)
        return hashlib.sha256(signature_str.encode()).hexdigest()
    
    def _text_based_search(
        self,
        pack_id: UUID,
        query_text: str,
        topic_id: Optional[str],
        top_k: int
    ) -> List[VectorHit]:
        """
        Fallback text-based search when vector search isn't available (e.g., fake embeddings).
        Searches chunks by keyword matching and returns top_k results.
        """
        # Extract keywords from query text
        keywords = [w.lower().strip() for w in query_text.split() if len(w) > 2]
        
        # Query chunks from published documents in this pack
        query = self.db.query(Chunk).join(Document).filter(
            Document.pack_id == pack_id,
            Document.status == "published",
            Chunk.embedding_v.isnot(None)  # Only chunks with embeddings
        )
        
        if topic_id:
            query = query.filter(Chunk.topic_id == topic_id)
        
        # Score chunks by keyword matches
        chunks = query.limit(top_k * 2).all()  # Get more to filter
        
        scored_chunks = []
        for chunk in chunks:
            text_lower = chunk.text.lower()
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0 or not keywords:  # Include all if no keywords or if matches found
                scored_chunks.append((score, chunk))
        
        # Sort by score (descending) and take top_k
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_chunks = [chunk for _, chunk in scored_chunks[:top_k]]
        
        # Convert to VectorHit format (include page range in metadata for citations)
        hits = []
        for chunk in top_chunks:
            text_lower = chunk.text.lower()
            match_count = sum(1 for kw in keywords if kw in text_lower) if keywords else 1
            similarity = min(1.0, 0.5 + (match_count / max(len(keywords), 1)) * 0.5)
            meta = dict(chunk.metadata_json or {})
            if chunk.page_start_pdf is not None:
                meta["page_start_pdf"] = chunk.page_start_pdf
            if chunk.page_end_pdf is not None:
                meta["page_end_pdf"] = chunk.page_end_pdf
            hits.append(VectorHit(
                chunk_id=chunk.chunk_id,
                document_id=str(chunk.document_id),
                text=chunk.text,
                similarity_score=similarity,
                metadata=meta if meta else None
            ))
        
        logger.info(f"Text-based search returned {len(hits)} chunks for query: {query_text}")
        return hits
    
    def _generate_simple_worksheet(
        self,
        chunks: List[str],
        topic_text: str,
        num_questions: int
    ) -> Dict[str, Any]:
        """
        Generate a simple worksheet from chunks without LLM.
        Creates basic comprehension questions from the content.
        """
        questions = []
        answer_key = {}
        marking_scheme = {}
        
        # Use first few chunks to generate questions
        content_text = "\n".join(chunks[:5])  # Use first 5 chunks
        
        # Simple question generation: create questions based on sentences in content
        sentences = [s.strip() for s in content_text.split('.') if len(s.strip()) > 20][:num_questions]
        
        for i, sentence in enumerate(sentences[:num_questions], 1):
            q_id = f"q{i}"
            
            # Create a simple comprehension question
            question_text = f"Based on the content, explain: {sentence[:100]}..."
            
            questions.append({
                "id": q_id,
                "type": "short_answer",
                "question": question_text,
                "correct_answer": sentence[:200],  # Required field
                "explanation": f"This answer is based on the content: {sentence[:150]}...",
                "points": 2,
                "difficulty": "medium",
                "math_content": False
            })
            
            answer_key[q_id] = sentence[:200]  # Use sentence as answer
            marking_scheme[q_id] = {
                "points": 2,
                "criteria": "Answer should reference the content provided"
            }
        
        return {
            "questions": questions,
            "answer_key": answer_key,
            "marking_scheme": marking_scheme,
            "citations": [{"chunk_id": f"chunk_{i}", "text": chunk[:100]} for i, chunk in enumerate(chunks[:3])]
        }
    
    def _normalize_topic_for_keywords(self, topic_text: str) -> str:
        """Normalize topic for keyword extraction (e.g. algebric -> algebraic). Keeps display as-is."""
        if not topic_text or not topic_text.strip():
            return topic_text or ""
        t = topic_text.strip().lower()
        # Common misspellings / variants
        replacements = {"algebric": "algebraic", "algabraic": "algebraic", "algerbraic": "algebraic"}
        for wrong, right in replacements.items():
            t = t.replace(wrong, right)
        return t

    def _expand_query_synonyms(self, topic_text: str) -> List[str]:
        """Expand topic with synonyms for retrieval. Normalize typos (algebric -> algebraic)."""
        normalized = self._normalize_topic_for_keywords(topic_text or "")
        topic_lower = (topic_text or "").lower() + " " + normalized
        out = []
        # Base terms from normalized topic
        out.extend(re.findall(r"[a-zA-Z0-9]+", normalized))
        # Algebraic expression: full synonym set
        if "algebra" in topic_lower or "expression" in topic_lower:
            out.extend([
                "algebra", "expression", "algebraic term", "variable", "coefficient", "constant",
                "simplify expression", "like terms", "unlike terms", "evaluate expression",
                "substitution", "distributive property", "algebraic expression",
                "term", "simplify", "evaluate", "translate words to expression",
            ])
        # Prime/factors
        if "prime" in topic_lower or "factor" in topic_lower:
            out.extend(["prime", "factor", "factorization", "composite", "hcf", "lcm"])
        # Sets
        if "set" in topic_lower:
            out.extend(["set", "element", "subset", "union", "intersection"])
        # Minimal Urdu/roman (common in PK curricula)
        if "algebra" in topic_lower or "expression" in topic_lower:
            out.extend(["jabar", "ibarat"])  # algebra, expression in Urdu roman
        return list(dict.fromkeys(w for w in out if len(w) > 1))[:25]

    def _extract_topic_keywords(self, topic_text: str) -> List[str]:
        """Extract keywords from topic for relevance and validation. Generic, no hardcoded topics."""
        normalized = self._normalize_topic_for_keywords(topic_text or "")
        words = re.findall(r"[a-zA-Z0-9]+", normalized)
        keywords = [w.lower() for w in words if len(w) >= 2 and w.lower() not in ("the", "and", "for", "from", "with", "this", "that")]
        topic_lower = (topic_text or "").lower() + " " + normalized
        if "algebra" in topic_lower or "expression" in topic_lower:
            keywords.extend(["algebraic", "expression", "term", "coefficient", "variable", "constant", "simplify", "evaluate", "like", "unlike", "translate"])
        if "prime" in topic_lower or "factor" in topic_lower:
            keywords.extend(["prime", "factor", "factorization", "composite", "hcf", "lcm"])
        if "set" in topic_lower:
            keywords.extend(["set", "element", "subset", "union", "intersection"])
        return list(dict.fromkeys(keywords))

    def _log_validation_fail_debug(
        self,
        normalized_topic_text: str,
        expanded_query_terms: List[str],
        top5_ranges: List[Tuple[Tuple[int, int], float]],
        final_page_range: Tuple[int, int],
        hits: List[VectorHit],
    ) -> None:
        """Log debug dump when topic validation fails (server logs)."""
        logger.warning(
            "[VALIDATION_FAIL DEBUG] normalized_topic_text=%s | expanded_query_terms=%s",
            normalized_topic_text, expanded_query_terms[:15],
        )
        logger.warning(
            "[VALIDATION_FAIL DEBUG] top 5 chapter candidate ranges (score): %s",
            [(r, round(s, 4)) for r, s in top5_ranges],
        )
        logger.warning(
            "[VALIDATION_FAIL DEBUG] final selected page_range(s): %s-%s",
            final_page_range[0], final_page_range[1],
        )
        for i, h in enumerate(hits[:15]):
            meta = h.metadata or {}
            start = meta.get("page_start_pdf")
            end = meta.get("page_end_pdf")
            pr = f"{start}-{end}" if start is not None and end is not None else str(start or end or "")
            sim = getattr(h, "similarity_score", None)
            text_preview = (h.text or "")[:200]
            logger.warning(
                "[VALIDATION_FAIL DEBUG] chunk[%s] chunk_id=%s page=%s similarity=%s text_preview=%s",
                i, h.chunk_id, pr, sim, text_preview,
            )

    def _raise_topic_not_found(
        self,
        top5_ranges: List[Tuple[Tuple[int, int], float]],
        chosen_ranges: List[Tuple[int, int]],
        hits_after_front: List[VectorHit],
        topic_text: str,
        relevance_hits: Optional[List[VectorHit]] = None,
        avg_sim: float = 0.0,
        keyword_hits: int = 0,
    ) -> None:
        """Raise 422 with TOPIC_NOT_FOUND_IN_PACK and top 3 closest ranges + why insufficient."""
        keywords = self._extract_topic_keywords(topic_text)
        top3 = top5_ranges[:3]
        parts = []
        for (lo, hi), score in top3:
            range_hits = [h for h in hits_after_front if (h.metadata or {}).get("page_start_pdf") is not None and lo <= (h.metadata or {}).get("page_start_pdf", 0) <= hi]
            r_sim, r_kw = self._relevance_score(range_hits, topic_text) if range_hits else (0.0, 0)
            parts.append(f"pages {lo}-{hi}: score={score:.3f}, avg_sim={r_sim:.3f}, keyword_hits={r_kw} (need avg_sim>=0.32, keyword_hits>=2)")
        msg = "TOPIC_NOT_FOUND_IN_PACK: No chapter with sufficient relevance. Closest ranges: " + "; ".join(parts)
        if relevance_hits is not None:
            msg += f" Best attempt had avg_sim={avg_sim:.3f}, keyword_hits={keyword_hits}."
        raise ValueError(msg)

    def _relevance_score(self, hits: List[VectorHit], topic_text: str) -> Tuple[float, int]:
        """Return (avg_similarity, keyword_hit_count) for topic relevance gate."""
        if not hits:
            return 0.0, 0
        keywords = self._extract_topic_keywords(topic_text)
        avg_sim = sum(getattr(h, "similarity_score", 0) for h in hits) / len(hits)
        context_text = " ".join(h.text for h in hits).lower()
        hit_count = sum(1 for kw in keywords if kw in context_text)
        return avg_sim, hit_count

    def _build_allowed_forbidden(self, context_text: str, topic_text: str) -> Tuple[List[str], List[str]]:
        """Build allowed concepts (from context) and forbidden concepts (unless in topic)."""
        # Extract top terms from context (words with 4+ chars, not stopwords)
        words = re.findall(r"[a-zA-Z]+", context_text.lower())
        stop = {"the", "and", "for", "from", "with", "this", "that", "which", "when", "what", "have", "has", "been", "were", "will", "your", "that", "they", "them"}
        freq = defaultdict(int)
        for w in words:
            if len(w) >= 4 and w not in stop:
                freq[w] += 1
        allowed = [w for w, _ in sorted(freq.items(), key=lambda x: -x[1])[:15]]
        # Forbidden: generic math that causes drift unless topic mentions them
        topic_lower = (topic_text or "").lower()
        forbidden_default = ["hcf", "lcm", "highest common factor", "lowest common multiple", "prime factorization", "prime number", "composite number", "absolute value", "integers", "integer"]
        forbidden = [f for f in forbidden_default if f.replace(" ", "") not in topic_lower.replace(" ", "")]
        return allowed, forbidden

    def _validate_questions_topic(self, questions: List[Dict[str, Any]], topic_text: str) -> Tuple[bool, str]:
        """Validate that questions match topic. Return (passed, report)."""
        if not questions:
            return False, "No questions to validate."
        keywords = self._extract_topic_keywords(topic_text)
        topic_lower = (topic_text or "").lower()
        normalized = self._normalize_topic_for_keywords(topic_text or "")
        # Forbidden drift terms (unless in topic)
        drift_terms = ["hcf", "lcm", "prime number", "composite", "factorization", "absolute value", "integer"]
        if "prime" in topic_lower or "factor" in topic_lower:
            drift_terms = [t for t in drift_terms if t not in ("prime number", "composite", "factorization", "hcf", "lcm")]
        match_count = 0
        drift_violations = []
        algebraic_ok = True
        for i, q in enumerate(questions):
            qtext = (q.get("question") or q.get("question_text") or "").lower()
            if any(kw in qtext for kw in keywords):
                match_count += 1
            for term in drift_terms:
                if term in qtext and term not in topic_lower:
                    drift_violations.append(f"Q{i+1}: contains '{term}'")
            # Algebraic expression: must have variable/expression vocab or symbols
            if "algebra" in normalized or "expression" in topic_lower:
                has_var = any(x in qtext for x in ["x", "y", "variable", "coefficient", "term", "simplify", "evaluate", "expression", "2x", "3y", "like terms"])
                if not has_var and len(qtext) > 20:
                    algebraic_ok = False
        need_match = max(7, int(len(questions) * 0.7))
        passed = match_count >= need_match and not drift_violations and (algebraic_ok or "algebra" not in normalized)
        report = f"Topic match: {match_count}/{len(questions)} (need {need_match})."
        if drift_violations:
            report += " Drift: " + "; ".join(drift_violations[:5])
        if not algebraic_ok and ("algebra" in normalized or "expression" in topic_lower):
            report += " Algebraic questions should use variables/expressions."
        return passed, report

    def get_worksheet(self, worksheet_id: UUID) -> Optional[WorksheetCache]:
        """Get cached worksheet by ID."""
        return self.db.query(WorksheetCache).filter(
            WorksheetCache.id == worksheet_id
        ).first()
