"""
Adapter: build Pipeline2 Teacher_profile text from DB feature snapshot (V1).

Used by Learning Hub / Pipeline2IntegrationService to run inference from
teacher_intelligence feature snapshots without rewriting the CSV/CLI path.

Does NOT modify dataset.py or the CSV load path. Additive only.
"""
from __future__ import annotations

from typing import Any, Dict


def snapshot_features_to_teacher_profile(features: Dict[str, Any]) -> str:
    """
    Build a single Teacher_profile-style text from a DB feature snapshot dict.

    The result is compatible with Pipeline2Model.predict() which expects
    a DataFrame with a Teacher_profile column. This string is used as that
    single row so the same embedding + KMeans path runs unchanged.

    Features dict is the teacher_intelligence feature snapshot schema (V1):
    country, region, subject_primary, grade_band, curriculum_framework,
    years_experience_bucket, certifications_count, education_level,
    experience_records, school_type, has_resume, has_portfolio.
    """
    subject = str(features.get("subject_primary") or "unknown")
    grade = str(features.get("grade_band") or "unknown")
    years = str(features.get("years_experience_bucket") or "unknown")
    school_type = str(features.get("school_type") or "unknown")
    region = str(features.get("region") or "unknown")
    curriculum = str(features.get("curriculum_framework") or "unknown")
    education_level = str(features.get("education_level") or "unknown")
    exp_records = int(features.get("experience_records") or 0)
    certs = int(features.get("certifications_count") or 0)

    return (
        f"Teaches {subject} to {grade} grade. "
        f"Years experience: {years}. "
        f"School type: {school_type}. "
        f"Region: {region}. "
        f"Curriculum: {curriculum}. "
        f"Education level: {education_level}. "
        f"Experience records: {exp_records}. "
        f"Certifications: {certs}."
    )
