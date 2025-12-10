"""
Execution service for templates with stubbed (fake) or real LLM output.
"""
import json
import time
import uuid
from typing import Any, Dict, Optional, Tuple, AsyncIterator

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.llm.config import llm_settings
from app.llm.router import ModelRouter
from app.llm.cache import ResponseCache
from app.llm.rate_limiter import RateLimiter
from app.llm.cost_tracker import CostTracker
from app.llm.toon_handler import TOONHandler
from app.llm.prompt_builder import TOONPromptBuilder
from app.models.template import Template, TemplateCategory
from app.models.template_version import TemplateVersion
from app.models.template_execution import TemplateExecution
from app.schemas.template import (
    UniversalTemplateOutput,
    LessonStep,
    BloomAlignmentItem,
    BloomLevel,
    AssessmentSection,
    AssessmentQuestion,
    CommunicationSection,
)

logger = get_logger(__name__)


class ExecutionService:
    """
    Service responsible for executing templates.

    Can use either stubbed output (default) or real LLM (when USE_REAL_LLM=True).
    """

    DUMMY_MODEL_USED = "stub-model"
    DUMMY_PROVIDER_USED = "stub-provider"
    
    _model_router: Optional[ModelRouter] = None
    _toon_handler: Optional[TOONHandler] = None
    _prompt_builder: Optional[TOONPromptBuilder] = None
    _cache: Optional[ResponseCache] = None
    _rate_limiter: Optional[RateLimiter] = None
    _cost_tracker: Optional[CostTracker] = None
    
    @classmethod
    def _get_model_router(cls) -> ModelRouter:
        """Get or create model router instance with cache, rate limiter, and cost tracker."""
        if cls._model_router is None:
            # Initialize cache
            if cls._cache is None and llm_settings.CACHE_ENABLED:
                cls._cache = ResponseCache(
                    ttl_seconds=llm_settings.CACHE_TTL_SECONDS,
                    redis_url=llm_settings.REDIS_URL
                )
            
            # Initialize rate limiter
            if cls._rate_limiter is None and llm_settings.RATE_LIMIT_ENABLED:
                cls._rate_limiter = RateLimiter(llm_settings)
            
            # Initialize cost tracker
            if cls._cost_tracker is None and llm_settings.COST_TRACKING_ENABLED:
                cls._cost_tracker = CostTracker()
            
            cls._model_router = ModelRouter(
                config=llm_settings,
                cache=cls._cache,
                rate_limiter=cls._rate_limiter,
                cost_tracker=cls._cost_tracker,
            )
        return cls._model_router
    
    @classmethod
    def _get_toon_handler(cls) -> TOONHandler:
        """Get or create TOON handler instance."""
        if cls._toon_handler is None:
            cls._toon_handler = TOONHandler()
        return cls._toon_handler
    
    @classmethod
    def _get_prompt_builder(cls) -> TOONPromptBuilder:
        """Get or create prompt builder instance."""
        if cls._prompt_builder is None:
            cls._prompt_builder = TOONPromptBuilder(cls._get_toon_handler())
        return cls._prompt_builder

    @classmethod
    def _build_stub_output(
        cls,
        template: Template,
        template_version: Optional[TemplateVersion],
        input_data: Dict[str, Any],
    ) -> UniversalTemplateOutput:
        """Build a fake but structurally correct UniversalTemplateOutput."""
        topic = input_data.get("topic", template.name)
        learning_objective = input_data.get("learning_objective", "Support student learning.")
        subject = input_data.get("subject", getattr(template, "subject_default", "general"))

        overview = f"{template.name} for {subject}: {topic}"
        learning_goals = [
            learning_objective,
            f"Help students engage deeply with {topic}.",
        ]
        materials = [
            "Whiteboard or digital board",
            "Student notebooks or devices",
        ]

        steps = [
            LessonStep(
                title="Introduction & Activation of Prior Knowledge",
                description=f"Briefly introduce {topic} and ask students what they already know.",
            ),
            LessonStep(
                title="Guided Practice",
                description=f"Model the core skill or concept related to {topic} and work through an example together.",
            ),
            LessonStep(
                title="Independent or Small-Group Practice",
                description="Students apply the concept with teacher circulating for support.",
            ),
        ]

        differentiation = [
            "Offer sentence stems or visual supports for students who need additional scaffolding.",
            "Provide extension tasks for students who are ready for enrichment.",
        ]

        teacher_notes = [
            "Adjust pacing based on student responses and check-ins.",
            "Capture examples of strong student thinking to highlight during debrief.",
        ]

        bloom_alignment = [
            BloomAlignmentItem(
                level=BloomLevel.UNDERSTAND,
                description="Students explain the core idea in their own words.",
            ),
            BloomAlignmentItem(
                level=BloomLevel.APPLY,
                description="Students use the concept in a new example.",
            ),
        ]

        assessment: Optional[AssessmentSection] = AssessmentSection(
            checks_for_understanding=[
                "Cold-call a few students to explain the concept.",
                "Use exit tickets asking students to solve a short problem or respond to a prompt.",
            ],
            rubric=None,
        )

        questions: Optional[list[AssessmentQuestion]] = None
        communication: Optional[CommunicationSection] = None

        if template.category == TemplateCategory.ASSESSMENT:
            questions = [
                AssessmentQuestion(
                    question_text=f"Explain {topic} in your own words.",
                    type="short_answer",
                ),
                AssessmentQuestion(
                    question_text=f"Apply {topic} to a real-world scenario.",
                    type="open_ended",
                ),
            ]

        if template.category == TemplateCategory.COMMUNICATION:
            communication = CommunicationSection(
                subject_line=f"Update about our work on {topic}",
                message_body=f"We are currently working on {topic}. Here is how you can support at home.",
                key_details=[
                    f"Students are learning to: {learning_objective}",
                    "Look for opportunities to discuss this topic in everyday life.",
                ],
                call_to_action="Reply to this message if you have any questions or want specific suggestions.",
            )

        return UniversalTemplateOutput(
            overview=overview,
            learning_goals=learning_goals,
            materials=materials,
            steps=steps,
            differentiation=differentiation,
            assessment=assessment,
            teacher_notes=teacher_notes,
            bloom_alignment=bloom_alignment,
            questions=questions,
            communication=communication,
        )

    @classmethod
    def _build_prompt(
        cls,
        template: Template,
        template_version: TemplateVersion,
        input_data: Dict[str, Any],
    ) -> Tuple[str, str]:
        """
        Build prompt using TOON-aware prompt builder.
        
        Returns:
            Tuple of (system_message, user_prompt)
        """
        prompt_builder = cls._get_prompt_builder()
        prompt_definition = template_version.prompt_definition or {}
        
        system_message, user_prompt = prompt_builder.build_prompt(
            input_data=input_data,
            prompt_definition=prompt_definition,
            template_category=template.category,
            model_config=template_version.model_config,
        )
        
        return system_message, user_prompt

    @classmethod
    def _parse_llm_response(
        cls,
        content: str,
        template: Template,
        template_version: Optional[TemplateVersion] = None,
    ) -> UniversalTemplateOutput:
        """
        Parse LLM response into UniversalTemplateOutput using TOON handler.
        
        Uses TOONHandler to parse TOON format (with JSON fallback).
        """
        toon_handler = cls._get_toon_handler()
        
        try:
            # Get output schema if available
            schema = None
            if template_version and template_version.output_schema:
                schema = json.dumps(template_version.output_schema) if isinstance(template_version.output_schema, dict) else str(template_version.output_schema)
            
            # Parse using TOON handler (handles TOON and JSON fallback)
            parsed = toon_handler.parse_output(content, schema=schema)
            
            # Build UniversalTemplateOutput from parsed data
            return cls._build_output_from_dict(parsed, template)
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            # Fallback to stub output with minimal data
            return cls._build_stub_output(template, template_version=None, input_data={"topic": "Error parsing response"})

    @classmethod
    def _naive_parse_text(cls, text: str) -> Dict[str, Any]:
        """Very naive text parser - extracts basic structure from text."""
        # This is a placeholder - in production, use more sophisticated parsing
        return {
            "overview": text[:200] if len(text) > 200 else text,
            "learning_goals": ["Extracted from response"],
            "materials": ["Materials needed"],
            "steps": [{"title": "Step 1", "description": text[:500]}],
            "differentiation": ["Differentiation strategies"],
            "teacher_notes": ["See generated content"],
        }

    @classmethod
    def _build_output_from_dict(
        cls,
        data: Dict[str, Any],
        template: Template,
    ) -> UniversalTemplateOutput:
        """Build UniversalTemplateOutput from parsed dictionary."""
        # Extract steps
        steps = []
        if "steps" in data and isinstance(data["steps"], list):
            for step in data["steps"]:
                if isinstance(step, dict):
                    steps.append(LessonStep(
                        title=step.get("title", "Step"),
                        description=step.get("description", "")
                    ))
                elif isinstance(step, str):
                    steps.append(LessonStep(title="Step", description=step))
        
        # Extract bloom alignment
        bloom_alignment = []
        if "bloom_alignment" in data and isinstance(data["bloom_alignment"], list):
            for item in data["bloom_alignment"]:
                if isinstance(item, dict):
                    level_str = item.get("level", "understand")
                    try:
                        level = BloomLevel(level_str)
                    except ValueError:
                        level = BloomLevel.UNDERSTAND
                    bloom_alignment.append(BloomAlignmentItem(
                        level=level,
                        description=item.get("description", "")
                    ))
        
        # Extract assessment
        assessment = None
        if "assessment" in data and isinstance(data["assessment"], dict):
            assessment = AssessmentSection(
                checks_for_understanding=data["assessment"].get("checks_for_understanding", []),
                rubric=data["assessment"].get("rubric")
            )
        
        # Extract questions (for assessment templates)
        questions = None
        if template.category == TemplateCategory.ASSESSMENT and "questions" in data:
            if isinstance(data["questions"], list):
                questions = []
                for q in data["questions"]:
                    if isinstance(q, dict):
                        questions.append(AssessmentQuestion(
                            question_text=q.get("question_text", ""),
                            type=q.get("type", "short_answer"),
                            answer_key=q.get("answer_key"),
                            difficulty=q.get("difficulty")
                        ))
        
        # Extract communication (for communication templates)
        communication = None
        if template.category == TemplateCategory.COMMUNICATION and "communication" in data:
            if isinstance(data["communication"], dict):
                comm_data = data["communication"]
                communication = CommunicationSection(
                    subject_line=comm_data.get("subject_line", ""),
                    message_body=comm_data.get("message_body", ""),
                    key_details=comm_data.get("key_details", []),
                    call_to_action=comm_data.get("call_to_action", "")
                )
        
        try:
            return UniversalTemplateOutput(
                overview=data.get("overview", "") or "Generated content",
                learning_goals=data.get("learning_goals", []) or [],
                materials=data.get("materials", []) or [],
                steps=steps if steps else [LessonStep(title="Step 1", description="See generated content")],
                differentiation=data.get("differentiation", []) or [],
                assessment=assessment,
                teacher_notes=data.get("teacher_notes", []) or [],
                bloom_alignment=bloom_alignment if bloom_alignment else [],
                questions=questions,
                communication=communication,
            )
        except Exception as e:
            logger.error(f"Error building UniversalTemplateOutput: {e}, data keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
            # Return minimal valid output
            return UniversalTemplateOutput(
                overview=data.get("overview", "Generated content") if isinstance(data, dict) else "Generated content",
                learning_goals=[],
                materials=[],
                steps=[LessonStep(title="Step 1", description="See generated content")],
                differentiation=[],
                assessment=None,
                teacher_notes=[],
                bloom_alignment=[],
                questions=None,
                communication=None,
            )

    @classmethod
    async def execute(
        cls,
        db: Session,
        *,
        template: Template,
        template_version: TemplateVersion,
        input_data: Dict[str, Any],
        user_id: Optional[uuid.UUID] = None,
        tenant_id: Optional[uuid.UUID] = None,
        is_demo: bool = False,
    ) -> Tuple[TemplateExecution, UniversalTemplateOutput]:
        """
        Execute a template with stubbed or real LLM output and persist a TemplateExecution.

        Returns the persisted TemplateExecution and the universal output model.
        """
        start_time = time.perf_counter()

        # Check if we should use real LLM
        use_real_llm = llm_settings.USE_REAL_LLM

        if use_real_llm:
            # Use real LLM
            logger.info(f"Using real LLM with TOON for template execution: {template.slug}")
            
            # Build prompt using TOON-aware prompt builder
            system_message, user_prompt = cls._build_prompt(template, template_version, input_data)
            
            # Get model config from template version
            model_config = template_version.model_config
            
            # Call LLM via router (async)
            router = cls._get_model_router()
            llm_response = await router.generate(
                system_message=system_message,
                prompt=user_prompt,
                model_config=model_config,
            )
            
            # Parse response using TOON handler
            universal_output = cls._parse_llm_response(llm_response.content, template, template_version)
            
            # Extract metadata from LLM response
            model_used = llm_response.model_used
            provider_used = llm_response.provider
            token_usage_dict = {
                "prompt": llm_response.token_usage.prompt if llm_response.token_usage else 0,
                "completion": llm_response.token_usage.completion if llm_response.token_usage else 0,
                "total": llm_response.token_usage.total if llm_response.token_usage else 0,
            }
            latency_ms = llm_response.latency_ms
            cost_estimate = llm_response.cost_estimate
            
        else:
            # Use stubbed output
            logger.info(f"Using stubbed output for template execution: {template.slug}")
            universal_output = cls._build_stub_output(
                template=template,
                template_version=template_version,
                input_data=input_data,
            )
            model_used = cls.DUMMY_MODEL_USED
            provider_used = cls.DUMMY_PROVIDER_USED
            token_usage_dict = {"prompt": 0, "completion": 0, "total": 0}
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            cost_estimate = 0

        execution = TemplateExecution(
            template_id=template.id,
            template_version_id=template_version.id,
            template_version=template_version.version,
            user_id=user_id,
            tenant_id=tenant_id,
            input_data=input_data,
            output_data=universal_output.model_dump(),
            model_used=model_used,
            provider_used=provider_used,
            token_usage=token_usage_dict,
            cost_estimate=cost_estimate,
            latency_ms=latency_ms,
            cache_hit=getattr(llm_response, 'cache_hit', False),
            alignment_flags=None,
        )

        db.add(execution)
        db.commit()
        db.refresh(execution)

        return execution, universal_output

    @classmethod
    async def execute_stream(
        cls,
        db: Session,
        *,
        template: Template,
        template_version: TemplateVersion,
        input_data: Dict[str, Any],
        user_id: Optional[uuid.UUID] = None,
        tenant_id: Optional[uuid.UUID] = None,
        is_demo: bool = False,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Execute a template with streaming LLM output, yielding domain events.

        Yields structured domain events (JSON-serializable dictionaries):
        - {"type": "meta", "template_slug": "...", "timestamp": "..."}
        - {"type": "content", "chunk": "..."}
        - {"type": "done", "execution_id": "...", "template_slug": "..."}
        - {"type": "error", "message": "...", "template_slug": "..."}

        Args:
            db: Database session
            template: Template instance
            template_version: TemplateVersion instance
            input_data: Input data dictionary
            user_id: Optional user ID
            tenant_id: Optional tenant ID
            is_demo: Whether this is a demo execution

        Yields:
            Domain events as dictionaries
        """
        start_time = time.perf_counter()
        
        # Emit meta event
        yield {
            "type": "meta",
            "template_slug": template.slug,
            "template_name": template.name,
            "timestamp": time.time(),
        }

        # Check if we should use real LLM
        use_real_llm = llm_settings.USE_REAL_LLM

        if not use_real_llm:
            # For stub mode, generate stub output and convert to markdown
            universal_output = cls._build_stub_output(
                template=template,
                template_version=template_version,
                input_data=input_data,
            )
            
            # Convert stub output to markdown (like Activity)
            from app.utils.markdown_converter import universal_output_to_markdown
            markdown_text = universal_output_to_markdown(universal_output.model_dump())
            
            # Stream markdown word-by-word (like Activity's stream_markdown_word_by_word)
            # CRITICAL: Stream exactly like Activity - no filtering, preserve all markdown characters including "#"
            if markdown_text:
                words = markdown_text.split(' ')
                for i, word in enumerate(words):
                    # CRITICAL: Don't filter - Activity streams everything including "#", "##", etc.
                    if i == 0:
                        chunk_to_send = word
                    else:
                        chunk_to_send = ' ' + word
                    
                    yield {
                        "type": "content",
                        "chunk": chunk_to_send,
                        "template_slug": template.slug,
                    }
            
            # Create execution record
            execution = TemplateExecution(
                template_id=template.id,
                template_version_id=template_version.id,
                template_version=template_version.version,
                user_id=user_id,
                tenant_id=tenant_id,
                input_data=input_data,
                output_data=universal_output.model_dump(),
                model_used=cls.DUMMY_MODEL_USED,
                provider_used=cls.DUMMY_PROVIDER_USED,
                token_usage={"prompt": 0, "completion": 0, "total": 0},
                cost_estimate=0,
                latency_ms=int((time.perf_counter() - start_time) * 1000),
                cache_hit=False,
                alignment_flags=None,
            )
            db.add(execution)
            db.commit()
            db.refresh(execution)
            
            yield {
                "type": "done",
                "execution_id": str(execution.id),
                "template_slug": template.slug,
            }
            return

        # Real LLM streaming path
        try:
            logger.info(f"Streaming LLM execution for template: {template.slug}")
            
            # CRITICAL: For streaming, use markdown prompt (like Activity)
            # This allows real-time streaming without waiting for complete TOON
            from app.llm.prompt_builder import TOONPromptBuilder
            prompt_builder = TOONPromptBuilder()
            
            # Build streaming prompt that generates markdown directly
            system_message, streaming_prompt = prompt_builder.build_streaming_prompt(
                input_data=input_data,
                prompt_definition=template_version.prompt_definition or {},
                template_category=template.category,
            )
            
            # Get model config from template version
            model_config = template_version.model_config
            
            # Get router
            router = cls._get_model_router()
            
            model_used = None
            provider_used = None
            token_usage_dict = {"prompt": 0, "completion": 0, "total": 0}
            
            # CRITICAL: Stream chunks directly from LLM (like Activity)
            # No TOON accumulation - stream markdown chunks immediately
            async for chunk in router.stream(
                system_message=system_message,
                prompt=streaming_prompt,
                model_config=model_config,
            ):
                # Stream chunks directly to frontend (real-time, no delays)
                if chunk:
                    yield {
                        "type": "content",
                        "chunk": chunk,
                        "template_slug": template.slug,
                    }
            
            # Stream completed
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            
            # For streaming, we don't need to parse TOON or build output
            # The markdown was streamed directly to frontend
            logger.info(f"Streaming completed in {latency_ms}ms")
            
            # Get metadata from router
            model_used = model_config.get("model") if model_config else llm_settings.DEFAULT_MODEL
            provider_used = model_config.get("provider") if model_config else llm_settings.DEFAULT_MODEL_PROVIDER
            
            # Create minimal execution record (no output_data for streaming)
            execution = TemplateExecution(
                template_id=template.id,
                template_version_id=template_version.id,
                template_version=template_version.version,
                user_id=user_id,
                tenant_id=tenant_id,
                input_data=input_data,
                output_data={},  # Empty for streaming (content was streamed, not stored)
                model_used=model_used,
                provider_used=provider_used,
                token_usage={"prompt": 0, "completion": 0, "total": 0},  # Estimate if needed
                cost_estimate=0.0,
                latency_ms=latency_ms,
                cache_hit=False,
                alignment_flags=None,
            )
            
            db.add(execution)
            db.commit()
            db.refresh(execution)
            
            # Emit done event
            yield {
                "type": "done",
                "execution_id": str(execution.id),
                "template_slug": template.slug,
            }
            
        except Exception as e:
            logger.error(f"Streaming execution error for template {template.slug}: {e}", exc_info=True)
            
            # Emit error event
            yield {
                "type": "error",
                "message": f"Error during template execution: {str(e)}",
                "template_slug": template.slug,
            }


