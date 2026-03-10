"""
SQLAlchemy base class for all models.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


# Import all models here so Alembic can discover them
from app.models.template import Template  # noqa: F401, E402
from app.models.template_version import TemplateVersion  # noqa: F401, E402
from app.models.template_execution import TemplateExecution  # noqa: F401, E402

# Import auth models
from app.domains.auth.models import (  # noqa: F401, E402
    Tenant,
    User,
    Role,
    Permission,
    RolePermission,
    UserRole,
    RefreshToken,
    PasswordResetToken,
    EmailVerificationToken,
    ParentStudentLink,
    Institution,
    PersonalWorkspace,
    UserMembership,
    Invite,
    AuditLog,
    TeacherProfileContext,
)

# Import subscription models
from app.domains.subscriptions.models import (  # noqa: F401, E402
    SubscriptionTierModel,
    SubscriptionTierFeature,
    UserSubscription,
    SubscriptionHistory,
    UserUsageQuota,
    UserUsageLog,
)

# Import chatbot models
from app.domains.chatbots.models import (  # noqa: F401, E402
    Chatbot,
    ChatbotModelAssignment,
    ChatbotCapability,
    ChatbotConversation,
    ChatbotMessage,
    ChatbotModelUsage,
    UserCapabilityProgress,
)

# Import content ingestion models
from app.domains.content_ingestion.models import (  # noqa: F401, E402
    ContentPack,
    Document,
    PageText,
    Chunk,
    DocumentProcessingRun,
    QAValidation,
    WorksheetCache,
    WorksheetQuestionHash,
)

# Import teacher identity models
from app.domains.teacher_identity.models import (  # noqa: F401, E402
    TeacherExperience,
    TeacherEducation,
    TeacherCertification,
    TeacherAchievement,
    TeacherCareerDocument,
)

# Import teacher intelligence models
from app.domains.teacher_intelligence.models import (  # noqa: F401, E402
    TeacherFeatureSnapshot,
    MLOutput,
    PipelineRun,
)

# Import content registry models
from app.domains.content_registry.models import ContentRegistryItem  # noqa: F401, E402

# Import content factory models
from app.domains.content_factory.models import ContentGenerationJob  # noqa: F401, E402
