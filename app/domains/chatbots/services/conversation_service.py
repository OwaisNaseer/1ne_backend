"""
Conversation service for managing chatbot conversations.
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.core.logging import get_logger
from app.domains.chatbots.models import (
    Chatbot,
    ChatbotConversation,
    ChatbotMessage,
)

logger = get_logger(__name__)


class ConversationService:
    """Service for managing chatbot conversations."""

    def __init__(self, db: Session):
        self.db = db

    def get_conversation(self, conversation_id: UUID, user_id: UUID) -> Optional[ChatbotConversation]:
        """Get conversation by ID (ensuring user owns it)."""
        return self.db.query(ChatbotConversation).filter(
            and_(
                ChatbotConversation.id == conversation_id,
                ChatbotConversation.user_id == user_id,
            )
        ).first()

    def list_conversations(
        self,
        user_id: UUID,
        chatbot_id: Optional[UUID] = None,
        limit: int = 50,
    ) -> List[ChatbotConversation]:
        """List user's conversations, optionally filtered by chatbot."""
        query = self.db.query(ChatbotConversation).filter(
            ChatbotConversation.user_id == user_id
        )

        if chatbot_id:
            query = query.filter(ChatbotConversation.chatbot_id == chatbot_id)

        return query.order_by(desc(ChatbotConversation.updated_at)).limit(limit).all()

    def create_conversation(
        self,
        chatbot_id: UUID,
        user_id: UUID,
        tenant_id: Optional[UUID] = None,
        title: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> ChatbotConversation:
        """Create a new conversation."""
        conversation = ChatbotConversation(
            chatbot_id=chatbot_id,
            user_id=user_id,
            tenant_id=tenant_id,
            title=title or "New Conversation",
            metadata=metadata or {},
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def update_conversation(
        self,
        conversation_id: UUID,
        user_id: UUID,
        title: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Optional[ChatbotConversation]:
        """Update conversation (title, metadata)."""
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            return None

        if title is not None:
            conversation.title = title
        if metadata is not None:
            conversation.conversation_metadata = metadata or {}
        conversation.updated_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def delete_conversation(
        self,
        conversation_id: UUID,
        user_id: UUID,
    ) -> bool:
        """Delete a conversation."""
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            return False

        self.db.delete(conversation)
        self.db.commit()
        return True

    def generate_conversation_title(self, first_message: str) -> str:
        """Generate conversation title from first message."""
        if not first_message:
            return "New Conversation"

        words = first_message.split()[:6]
        title = " ".join(words)
        return title[:50] + "..." if len(title) > 50 else title
