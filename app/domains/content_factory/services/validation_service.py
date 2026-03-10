"""
Validation Service: validate generated content before publishing.
Rejects invalid outputs; no DB writes.
"""
from typing import Any, Dict, List

from app.core.logging import get_logger

logger = get_logger(__name__)


class ValidationServiceError(Exception):
    """Raised when validation fails."""
    pass


class ValidationService:
    """Validate final generated content: required fields, module structure, lesson count, assessment."""

    def validate_micro_course(self, full_content: Dict[str, Any]) -> List[str]:
        """
        Validate full_content (curriculum + pedagogy + structure + assessment).
        Returns list of error messages; empty list if valid.
        """
        errors: List[str] = []
        if not isinstance(full_content, dict):
            errors.append("Content must be a JSON object")
            return errors

        for key in ("curriculum", "pedagogy", "structure", "assessment"):
            if key not in full_content:
                errors.append("Missing required section: " + key)

        structure = full_content.get("structure") or {}
        if isinstance(structure, dict):
            modules = structure.get("modules")
            lessons = structure.get("lessons")
            if not (isinstance(modules, list) and len(modules) > 0):
                errors.append("At least one module is required")
            if not (isinstance(lessons, list) and len(lessons) > 0):
                errors.append("At least one lesson is required")
        else:
            errors.append("structure must be an object with modules and lessons")

        assessment = full_content.get("assessment") or {}
        if isinstance(assessment, dict):
            has_tasks = bool(assessment.get("practice_tasks"))
            has_prompts = bool(assessment.get("reflection_prompts"))
            if not has_tasks and not has_prompts:
                errors.append("Assessment must include practice_tasks or reflection_prompts")
        else:
            errors.append("assessment must be an object")

        if errors:
            logger.warning("Validation failed: %s", errors)
        return errors

    def validate_and_raise(self, full_content: Dict[str, Any]) -> None:
        """Validate and raise ValidationServiceError if invalid."""
        errors = self.validate_micro_course(full_content)
        if errors:
            raise ValidationServiceError("; ".join(errors))
