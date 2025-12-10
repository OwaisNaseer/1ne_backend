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

