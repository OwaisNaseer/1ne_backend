"""
Recommendation Mapping Service: map teacher intelligence to content registry items.
V1: deterministic, rule-based only. No LLMs.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.domains.content_registry.models import ContentRegistryItem
from app.domains.content_registry.schemas import RecommendationCard, RecommendationMappingResponse
from app.domains.content_registry.services.content_registry_service import ContentRegistryService
from app.domains.content_registry.enums import ContentType, ContentStatus
from app.domains.teacher_intelligence.services import (
    CTPAssemblerService,
    FeatureSnapshotService,
    MLOutputService,
)

# V1: prefer these content types for recommendations
PREFERRED_TYPES = [
    ContentType.MICRO_COURSE.value,
    ContentType.AI_GUIDED_TUTORIAL.value,
    ContentType.LEARNING_PATH.value,
]


def _item_to_card(
    item: ContentRegistryItem,
    score: Optional[float] = None,
    reason: Optional[str] = None,
    route: Optional[str] = None,
) -> RecommendationCard:
    """Build RecommendationCard from registry item."""
    if route is None:
        route = f"/learning-hub/content/{item.content_id}"
    return RecommendationCard(
        content_id=item.content_id,
        content_type=item.content_type,
        title=item.title,
        subtitle=item.subtitle,
        summary=item.summary,
        category=item.category,
        estimated_duration_min=item.estimated_duration_min,
        difficulty=item.difficulty,
        route=route,
        score=score,
        reason=reason,
    )


def _tags_or_alignment_match_goals(item: ContentRegistryItem, goals: List[str]) -> bool:
    """True if item tags/alignment overlap with teacher goals."""
    if not goals:
        return False
    goals_lower = [g.lower().strip() for g in goals if g]
    tags = item.tags or {}
    alignment = item.alignment or {}
    for d in (tags, alignment):
        if isinstance(d, dict):
            for v in d.values():
                if isinstance(v, str) and v.lower() in goals_lower:
                    return True
                if isinstance(v, list):
                    for x in v:
                        if isinstance(x, str) and x.lower() in goals_lower:
                            return True
    return False


class RecommendationMappingService:
    """Map teacher intelligence to content registry recommendations."""

    def __init__(self, db: Session):
        self.db = db

    def get_learning_hub_recommendations(
        self,
        teacher_id: UUID,
        locale: str = "en",
        limit: int = 6,
    ) -> RecommendationMappingResponse:
        """
        V1: Use ml_output.recommended_targets if present and matching content_id;
        else fall back to rules (goals, category, published, locale).
        Returns up to 3 primary + up to 3 secondary.
        """
        registry_svc = ContentRegistryService(self.db)
        output_svc = MLOutputService(self.db)
        assembler = CTPAssemblerService(self.db)

        primary: List[RecommendationCard] = []
        secondary: List[RecommendationCard] = []
        seen_ids: set = set()

        ml_output = output_svc.get_latest(teacher_id, pipeline_name="pipeline2")
        ctp = assembler.assemble(teacher_id)
        goals = ctp.get("goals") or []
        identity = ctp.get("identity") or {}
        subjects = identity.get("subjects") or []
        grade_band = identity.get("grade_band") or ""

        # 1) Direct targets from ml_output
        if ml_output and isinstance(ml_output.results, dict):
            targets = ml_output.results.get("recommended_targets") or []
            for t in targets:
                if len(primary) >= 3:
                    break
                if isinstance(t, dict):
                    target_id = t.get("target_id") or t.get("content_id")
                else:
                    target_id = str(t) if t else None
                if not target_id or target_id in seen_ids:
                    continue
                item = registry_svc.get_item_by_content_id(str(target_id))
                if item and item.status == ContentStatus.PUBLISHED.value and (not locale or item.locale == locale):
                    primary.append(
                        _item_to_card(
                            item,
                            score=t.get("score") if isinstance(t, dict) else None,
                            reason="Recommended by your learning profile",
                        )
                    )
                    seen_ids.add(item.content_id)

        # 2) Goal/category match (secondary or fill primary)
        published = registry_svc.list_items(
            status=ContentStatus.PUBLISHED.value,
            locale=locale,
            limit=20,
        )
        for item in published:
            if item.content_id in seen_ids:
                continue
            if item.content_type not in PREFERRED_TYPES:
                continue
            if _tags_or_alignment_match_goals(item, goals):
                card = _item_to_card(
                    item,
                    score=0.7,
                    reason="Matches your professional goals",
                )
                if len(primary) < 3:
                    primary.append(card)
                    seen_ids.add(item.content_id)
                elif len(secondary) < 3:
                    secondary.append(card)
                    seen_ids.add(item.content_id)
                if len(primary) >= 3 and len(secondary) >= 3:
                    break

        # 3) General published preferred type (fill remaining)
        for item in published:
            if item.content_id in seen_ids:
                continue
            if item.content_type not in PREFERRED_TYPES:
                continue
            card = _item_to_card(item, score=0.5, reason="Suggested for you")
            if len(primary) < 3:
                primary.append(card)
                seen_ids.add(item.content_id)
            elif len(secondary) < 3:
                secondary.append(card)
                seen_ids.add(item.content_id)
            if len(primary) >= 3 and len(secondary) >= 3:
                break

        return RecommendationMappingResponse(
            primary_recommendations=primary[:3],
            secondary_recommendations=secondary[:3],
        )
