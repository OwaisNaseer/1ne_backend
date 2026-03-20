"""
Learning Hub home orchestration (V1): build home payload from CTP, snapshot, ml_output, context.
Deterministic, rules-based; no LLMs. No content registry yet.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import UUID

from sqlalchemy.orm import Session

from app.domains.auth.models import TeacherProfileContext
from app.domains.teacher_intelligence.services import (
    CTPAssemblerService,
    FeatureSnapshotService,
    MLOutputService,
    IntelligenceRefreshService,
)
from app.domains.teacher_identity.models import (
    TeacherExperience,
    TeacherCertification,
    TeacherCareerDocument,
)
from app.domains.content_registry.services import RecommendationMappingService
from app.domains.learning_progress.services import ProgressAggregationService
from app.domains.learning_hub import schemas as hub_schemas

# Fields that count toward profile completeness (spec)
_COMPLETENESS_FIELDS = [
    "country",
    "region",
    "subjects",
    "grade_band",
    "school_type",
    "language_preference",
    "years_experience",
]

_COLD_START = "cold_start"
_WARM_START = "warm_start"
_PERSONALIZED = "personalized"


def _has_meaningful_profile_data(ctp: Dict[str, Any], profile_completeness: hub_schemas.ProfileCompleteness) -> bool:
    if not ctp:
        return False
    identity = ctp.get("identity") or {}
    environment = ctp.get("environment") or {}
    profile_fields = [
        identity.get("country"),
        identity.get("region"),
        identity.get("subjects"),
        identity.get("grade_band"),
        environment.get("school_type"),
        environment.get("language_preference"),
    ]
    populated = sum(1 for field in profile_fields if field)
    return populated >= 4 and profile_completeness.score >= 0.45


def _detect_learning_hub_mode(
    ctp: Dict[str, Any],
    snapshot: Any,
    ml_output: Any,
    profile_completeness: hub_schemas.ProfileCompleteness,
    progress_overview: Any,
) -> str:
    identity = ctp.get("identity") or {}
    environment = ctp.get("environment") or {}
    profile_ready = _has_meaningful_profile_data(ctp, profile_completeness)
    behavior_sessions = int(getattr(progress_overview, "total_sessions", 0) or 0) if progress_overview else 0
    behavior_completed = int(getattr(progress_overview, "completed_content_count", 0) or 0) if progress_overview else 0
    behavior_ready = behavior_sessions >= 4 and behavior_completed >= 1
    snapshot_ready = snapshot is not None
    ml_ready = ml_output is not None

    has_any_signal = any(
        [
            profile_ready,
            snapshot_ready,
            ml_ready,
            behavior_sessions > 0,
            bool(identity.get("subjects")),
            bool(identity.get("grade_band")),
            bool(environment.get("school_type")),
        ]
    )

    if profile_completeness.score < 0.45 and not behavior_ready and not snapshot_ready and not ml_ready:
        return _COLD_START

    if profile_ready and snapshot_ready and ml_ready and behavior_ready:
        return _PERSONALIZED

    if profile_ready or has_any_signal:
        return _WARM_START

    return _COLD_START


def _compute_profile_completeness(
    db: Session, teacher_id: UUID
) -> hub_schemas.ProfileCompleteness:
    """Score 0-1 and missing_fields from context + at least one identity record."""
    missing: List[str] = []
    ctx = None
    try:
        ctx = (
            db.query(TeacherProfileContext)
            .filter(TeacherProfileContext.user_id == teacher_id)
            .first()
        )
    except Exception:
        # Partial migrations / missing optional tables -> treat profile as incomplete.
        try:
            db.rollback()
        except Exception:
            pass
        return hub_schemas.ProfileCompleteness(
            score=0.0,
            missing_fields=list(_COMPLETENESS_FIELDS) + ["teaching_context"],
        )

    if not ctx:
        return hub_schemas.ProfileCompleteness(
            score=0.0,
            missing_fields=list(_COMPLETENESS_FIELDS) + ["teaching_context"],
        )

    if not (ctx.country and str(ctx.country).strip()):
        missing.append("country")
    if not (ctx.region and str(ctx.region).strip()):
        missing.append("region")
    if not (ctx.subjects and isinstance(ctx.subjects, list) and len(ctx.subjects) > 0):
        missing.append("subjects")
    if not (ctx.grade_band and str(ctx.grade_band).strip()):
        missing.append("grade_band")
    if not (ctx.school_type and str(ctx.school_type).strip()):
        missing.append("school_type")
    if not (ctx.language_preference and str(ctx.language_preference).strip()):
        missing.append("language_preference")
    if not (getattr(ctx, "years_experience", None) and str(ctx.years_experience or "").strip()):
        missing.append("years_experience")

    has_identity = False
    try:
        has_identity = (
            db.query(TeacherExperience).filter(TeacherExperience.user_id == teacher_id).first()
            or db.query(TeacherCertification).filter(TeacherCertification.user_id == teacher_id).first()
            or db.query(TeacherCareerDocument).filter(TeacherCareerDocument.user_id == teacher_id).first()
        )
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
        has_identity = False
    if not has_identity:
        missing.append("experience_or_certification_or_document")

    total_checks = len(_COMPLETENESS_FIELDS) + 1
    score = (total_checks - len(missing)) / total_checks if total_checks else 0.0
    return hub_schemas.ProfileCompleteness(score=max(0.0, min(1.0, score)), missing_fields=missing)


def _teacher_summary_from_ctp(ctp: Dict[str, Any]) -> hub_schemas.TeacherSummary:
    """Build teacher summary from CTP dict."""
    identity = ctp.get("identity") or {}
    environment = ctp.get("environment") or {}
    subjects = identity.get("subjects") or []
    return hub_schemas.TeacherSummary(
        subjects=subjects if isinstance(subjects, list) else [],
        grade_band=str(identity.get("grade_band") or ""),
        school_type=str(environment.get("school_type") or ""),
        region=str(identity.get("region") or ""),
        years_experience=str(environment.get("years_experience") or ""),
    )


def _intelligence_from_ml_output(ml_output: Any) -> hub_schemas.IntelligenceCard:
    """Build intelligence card from ML output record."""
    results = getattr(ml_output, "results", None) or {}
    return hub_schemas.IntelligenceCard(
        cluster_id=results.get("cluster_id"),
        persona_tag=results.get("persona_tag"),
        pipeline_version=getattr(ml_output, "pipeline_version", None),
        feature_schema_version=None,
    )


def _focus_areas_and_next_actions(
    db: Session,
    teacher_id: UUID,
    has_snapshot: bool,
    has_ml_output: bool,
    profile_completeness: hub_schemas.ProfileCompleteness,
) -> tuple[List[hub_schemas.FocusArea], List[hub_schemas.NextAction]]:
    """Rules-based focus areas and next actions."""
    focus_areas: List[hub_schemas.FocusArea] = []
    next_actions: List[hub_schemas.NextAction] = []

    if has_ml_output:
        focus_areas.append(
            hub_schemas.FocusArea(
                title="Personalized learning path",
                source="ml_output",
                priority=1,
            )
            # V1: no concrete content IDs; generic title
        )

    if not has_snapshot:
        next_actions.append(
            hub_schemas.NextAction(
                action_type="generate_feature_snapshot",
                label="Generate your learning profile",
                reason="Your feature snapshot is missing. Generate it to get personalized recommendations.",
            )
        )

    if profile_completeness.score < 1.0 and profile_completeness.missing_fields:
        if "teaching_context" in profile_completeness.missing_fields or any(
            f in profile_completeness.missing_fields for f in _COMPLETENESS_FIELDS
        ):
            next_actions.append(
                hub_schemas.NextAction(
                    action_type="complete_profile",
                    label="Complete your teaching context",
                    reason="Complete your profile for better recommendations.",
                )
            )
        if "experience_or_certification_or_document" in profile_completeness.missing_fields:
            next_actions.append(
                hub_schemas.NextAction(
                    action_type="add_career_data",
                    label="Add experience, certifications, or documents",
                    reason="Add career data to enrich your learning profile.",
                )
            )

    if not next_actions and has_snapshot and has_ml_output:
        next_actions.append(
            hub_schemas.NextAction(
                action_type="explore_recommendations",
                label="Explore recommendations",
                reason="Your profile is set up. Explore your personalized focus areas.",
            )
        )

    return focus_areas, next_actions


class LearningHubHomeService:
    """Build V1 Learning Hub home response from available intelligence."""

    def __init__(self, db: Session):
        self.db = db

    def get_home(self, teacher_id: UUID) -> hub_schemas.LearningHubHomeResponse:
        """Build deterministic home payload for the teacher. Ensures fresh intelligence first."""
        refresh_service = IntelligenceRefreshService(self.db)
        try:
            refresh_service.ensure_fresh_teacher_intelligence(teacher_id)
        except Exception:  # pragma: no cover - defensive
            # If intelligence tables aren’t present (e.g., partial migrations),
            # degrade gracefully to cold-start mode with seeded recommendations.
            try:
                self.db.rollback()
            except Exception:
                pass

        assembler = CTPAssemblerService(self.db)
        snapshot_svc = FeatureSnapshotService(self.db)
        output_svc = MLOutputService(self.db)
        progress_svc = ProgressAggregationService(self.db)

        ctp = {}
        try:
            ctp = assembler.assemble(teacher_id) or {}
        except Exception as exc:  # pragma: no cover - defensive
            # If optional CTP sources/tables are missing, fall back to cold-start mode.
            # We keep home deterministic and non-empty via seeded recommendations.
            ctp = {}
            try:
                self.db.rollback()
            except Exception:
                pass

        snapshot = None
        try:
            snapshot = snapshot_svc.get_latest(teacher_id)
        except Exception:  # pragma: no cover - defensive
            snapshot = None
            try:
                self.db.rollback()
            except Exception:
                pass

        ml_output = None
        try:
            ml_output = output_svc.get_latest(teacher_id, pipeline_name="pipeline2")
        except Exception:  # pragma: no cover - defensive
            ml_output = None
            try:
                self.db.rollback()
            except Exception:
                pass

        profile_completeness = _compute_profile_completeness(self.db, teacher_id)
        teacher_summary = _teacher_summary_from_ctp(ctp)

        if ml_output:
            intelligence = _intelligence_from_ml_output(ml_output)
            if snapshot:
                intelligence.feature_schema_version = getattr(
                    snapshot, "feature_schema_version", None
                )
        else:
            intelligence = hub_schemas.IntelligenceCard()

        focus_areas, next_actions = _focus_areas_and_next_actions(
            self.db,
            teacher_id,
            has_snapshot=snapshot is not None,
            has_ml_output=ml_output is not None,
            profile_completeness=profile_completeness,
        )

        mapping_svc = RecommendationMappingService(self.db)
        locale = "en"
        if ctp:
            identity = ctp.get("identity") or {}
            locale = str(identity.get("language_preference") or identity.get("locale") or "en").strip() or "en"
        progress_overview = None
        try:
            progress_overview = progress_svc.get_progress_overview(teacher_id)
        except Exception:  # pragma: no cover - defensive
            progress_overview = None
            try:
                self.db.rollback()
            except Exception:
                pass
        mode = _detect_learning_hub_mode(
            ctp=ctp,
            snapshot=snapshot,
            ml_output=ml_output,
            profile_completeness=profile_completeness,
            progress_overview=progress_overview,
        )
        rec_response = mapping_svc.get_learning_hub_recommendations(
            teacher_id=teacher_id,
            locale=locale,
            limit=6,
            mode=mode,
        )

        return hub_schemas.LearningHubHomeResponse(
            teacher_id=teacher_id,
            generated_at=datetime.now(timezone.utc),
            profile_completeness=profile_completeness,
            teacher_summary=teacher_summary,
            intelligence=intelligence,
            focus_areas=focus_areas,
            next_actions=next_actions,
            primary_recommendations=rec_response.primary_recommendations,
            secondary_recommendations=rec_response.secondary_recommendations,
            progress_overview=progress_overview.model_dump(),
            mode=mode,
        )
