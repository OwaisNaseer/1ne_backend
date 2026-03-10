"""
Content Registry Service: CRUD and publish for canonical content items.
"""
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.domains.content_registry.models import ContentRegistryItem
from app.domains.content_registry.schemas import ContentRegistryCreate, ContentRegistryUpdate
from app.domains.content_registry.enums import ContentStatus, ContentType

logger = get_logger(__name__)


class ContentRegistryServiceError(Exception):
    """Raised when registry operation fails (e.g. duplicate content_id)."""
    pass


class ContentRegistryService:
    """CRUD and publish for content registry items."""

    def __init__(self, db: Session):
        self.db = db

    def create_item(self, data: ContentRegistryCreate) -> ContentRegistryItem:
        """Create a new content registry item. Raises ContentRegistryServiceError if content_id exists."""
        existing = (
            self.db.query(ContentRegistryItem)
            .filter(ContentRegistryItem.content_id == data.content_id)
            .first()
        )
        if existing:
            raise ContentRegistryServiceError("Content ID already exists: " + data.content_id)

        item = ContentRegistryItem(
            content_id=data.content_id,
            content_type=data.content_type,
            schema_version=data.schema_version,
            content_version_major=data.content_version_major,
            content_version_minor=data.content_version_minor,
            content_version_patch=data.content_version_patch,
            locale=data.locale,
            status=data.status,
            title=data.title,
            subtitle=data.subtitle,
            summary=data.summary,
            category=data.category,
            estimated_duration_min=data.estimated_duration_min,
            difficulty=data.difficulty,
            impact_level=data.impact_level,
            tags=data.tags,
            alignment=data.alignment,
            json_blob=data.json_blob,
            source_type=data.source_type,
            source_ref=data.source_ref,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        logger.info("Created content registry item id=%s content_id=%s", item.id, item.content_id)
        return item

    def get_item_by_id(self, id: UUID) -> Optional[ContentRegistryItem]:
        """Get item by primary key."""
        return self.db.query(ContentRegistryItem).filter(ContentRegistryItem.id == id).first()

    def get_item_by_content_id(self, content_id: str) -> Optional[ContentRegistryItem]:
        """Get item by content_id."""
        return (
            self.db.query(ContentRegistryItem)
            .filter(ContentRegistryItem.content_id == content_id)
            .first()
        )

    def list_items(
        self,
        content_type: Optional[str] = None,
        status: Optional[str] = None,
        locale: Optional[str] = None,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ContentRegistryItem]:
        """List items with optional filters. Returns items only."""
        q = self.db.query(ContentRegistryItem)
        if content_type is not None:
            q = q.filter(ContentRegistryItem.content_type == content_type)
        if status is not None:
            q = q.filter(ContentRegistryItem.status == status)
        if locale is not None:
            q = q.filter(ContentRegistryItem.locale == locale)
        if category is not None:
            q = q.filter(ContentRegistryItem.category == category)
        if difficulty is not None:
            q = q.filter(ContentRegistryItem.difficulty == difficulty)
        return q.order_by(ContentRegistryItem.created_at.desc()).offset(skip).limit(limit).all()

    def update_item(self, id: UUID, data: ContentRegistryUpdate) -> Optional[ContentRegistryItem]:
        """Update item by id. Returns updated item or None."""
        item = self.get_item_by_id(id)
        if not item:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        logger.info("Updated content registry item id=%s", id)
        return item

    def delete_item(self, id: UUID) -> bool:
        """Hard delete item by id."""
        item = self.get_item_by_id(id)
        if not item:
            return False
        self.db.delete(item)
        self.db.commit()
        logger.info("Deleted content registry item id=%s", id)
        return True

    def publish_item(self, id: UUID) -> Optional[ContentRegistryItem]:
        """Set status=PUBLISHED and published_at if not set. Returns updated item or None."""
        item = self.get_item_by_id(id)
        if not item:
            return None
        item.status = ContentStatus.PUBLISHED.value
        if item.published_at is None:
            item.published_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(item)
        logger.info("Published content registry item id=%s", id)
        return item

    def seed_sample_content(self) -> List[ContentRegistryItem]:
        """
        Insert minimal sample items if not present: one MICRO_COURSE, one AI_GUIDED_TUTORIAL,
        one LEARNING_PATH. Idempotent (skips existing content_id). Returns list of created items.
        """
        created: List[ContentRegistryItem] = []
        samples = [
            {
                "content_id": "sample-micro-course-classroom-mgmt",
                "content_type": ContentType.MICRO_COURSE.value,
                "title": "Classroom Management Essentials",
                "subtitle": "Build a positive and productive learning environment.",
                "summary": "A short micro-course on core classroom management strategies.",
                "category": "classroom_management",
                "estimated_duration_min": 30,
                "difficulty": "beginner",
            },
            {
                "content_id": "sample-ai-tutorial-lesson-planning",
                "content_type": ContentType.AI_GUIDED_TUTORIAL.value,
                "title": "Lesson Planning with AI",
                "subtitle": "Design effective lessons with guided support.",
                "summary": "AI-guided tutorial for structuring and improving lesson plans.",
                "category": "lesson_planning",
                "estimated_duration_min": 45,
                "difficulty": "intermediate",
            },
            {
                "content_id": "sample-learning-path-assessment",
                "content_type": ContentType.LEARNING_PATH.value,
                "title": "Assessment Design",
                "subtitle": "From formative checks to summative assessments.",
                "summary": "A learning path covering assessment design and implementation.",
                "category": "assessment",
                "estimated_duration_min": 120,
                "difficulty": "intermediate",
            },
        ]
        for s in samples:
            if self.get_item_by_content_id(s["content_id"]):
                continue
            data = ContentRegistryCreate(
                content_id=s["content_id"],
                content_type=s["content_type"],
                schema_version="1.0",
                locale="en",
                status=ContentStatus.PUBLISHED.value,
                title=s["title"],
                subtitle=s.get("subtitle"),
                summary=s.get("summary"),
                category=s.get("category"),
                estimated_duration_min=s.get("estimated_duration_min"),
                difficulty=s.get("difficulty"),
            )
            item = self.create_item(data)
            published = self.publish_item(item.id)
            created.append(published if published else item)
        return created
