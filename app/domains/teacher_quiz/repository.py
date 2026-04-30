from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import desc, func, or_, cast, String
from sqlalchemy.orm import Session, joinedload

from app.domains.teacher_quiz.models import (
    TeacherQuiz,
    TeacherQuizGenerationRun,
    TeacherQuizQuestion,
)


@dataclass(frozen=True)
class QuizListFilters:
    q: str | None = None
    subject: str | None = None
    grade: str | None = None
    status: str | None = None
    class_key: str | None = None
    date_from: str | None = None  # YYYY-MM-DD
    date_to: str | None = None  # YYYY-MM-DD


class TeacherQuizRepository:
    def __init__(self, db: Session):
        self.db = db

    # ---------------------------------------------------------------------
    # Query helpers
    # ---------------------------------------------------------------------

    def list_quizzes(
        self,
        tenant_id: UUID,
        filters: QuizListFilters,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[TeacherQuiz], int]:
        q = self.db.query(TeacherQuiz).filter(TeacherQuiz.tenant_id == tenant_id)

        if filters.q:
            term = f"%{filters.q.lower()}%"
            q = q.filter(func.lower(TeacherQuiz.title).ilike(term))

        if filters.subject:
            q = q.filter(TeacherQuiz.subject == filters.subject)

        if filters.grade:
            q = q.filter(TeacherQuiz.grade == filters.grade)

        if filters.status:
            q = q.filter(TeacherQuiz.status == filters.status)

        if filters.class_key:
            # class_keys is JSONB list; for Postgres use JSON containment. For other
            # backends (tests), fall back to string contains.
            bind = self.db.get_bind()
            dialect = bind.dialect.name if bind is not None else ""
            if dialect == "postgresql":
                q = q.filter(TeacherQuiz.class_keys.contains([filters.class_key]))  # type: ignore[attr-defined]
            else:
                q = q.filter(cast(TeacherQuiz.class_keys, String).ilike(f"%{filters.class_key}%"))

        # Date filters apply to assigned dates (UI filter). For non-Postgres (tests),
        # we skip to keep queries portable.
        bind = self.db.get_bind()
        dialect = bind.dialect.name if bind is not None else ""
        if dialect == "postgresql":
            if filters.date_from:
                q = q.filter(
                    or_(
                        TeacherQuiz.assigned_at.is_(None),
                        func.to_char(TeacherQuiz.assigned_at, "YYYY-MM-DD") >= filters.date_from,
                    )
                )
            if filters.date_to:
                q = q.filter(
                    or_(
                        TeacherQuiz.assigned_at.is_(None),
                        func.to_char(TeacherQuiz.assigned_at, "YYYY-MM-DD") <= filters.date_to,
                    )
                )

        q = q.order_by(desc(TeacherQuiz.updated_at), desc(TeacherQuiz.created_at))

        total = q.count()
        offset = (page - 1) * page_size
        items = q.offset(offset).limit(page_size).all()
        return items, total

    def get_quiz(
        self,
        tenant_id: UUID,
        quiz_id: UUID,
        with_questions: bool = True,
    ) -> Optional[TeacherQuiz]:
        q = self.db.query(TeacherQuiz).filter(
            TeacherQuiz.tenant_id == tenant_id,
            TeacherQuiz.id == quiz_id,
        )
        if with_questions:
            q = q.options(joinedload(TeacherQuiz.questions))
        return q.first()

    def create_quiz(self, quiz: TeacherQuiz) -> TeacherQuiz:
        self.db.add(quiz)
        self.db.commit()
        self.db.refresh(quiz)
        return quiz

    def update_quiz(self, quiz: TeacherQuiz) -> TeacherQuiz:
        self.db.add(quiz)
        self.db.commit()
        self.db.refresh(quiz)
        return quiz

    def delete_quiz(self, quiz: TeacherQuiz) -> None:
        self.db.delete(quiz)
        self.db.commit()

    # ---------------------------------------------------------------------
    # Questions
    # ---------------------------------------------------------------------

    def replace_questions(
        self,
        quiz: TeacherQuiz,
        questions: Iterable[TeacherQuizQuestion],
    ) -> None:
        # Clear existing
        quiz.questions = []
        self.db.flush()
        quiz.questions = list(questions)
        self.db.add(quiz)
        self.db.commit()
        self.db.refresh(quiz)

    # ---------------------------------------------------------------------
    # Generation runs / idempotency
    # ---------------------------------------------------------------------

    def find_generation_run_by_idempotency(
        self,
        quiz_id: UUID,
        idempotency_key: str,
    ) -> Optional[TeacherQuizGenerationRun]:
        return (
            self.db.query(TeacherQuizGenerationRun)
            .filter(
                TeacherQuizGenerationRun.quiz_id == quiz_id,
                TeacherQuizGenerationRun.idempotency_key == idempotency_key,
            )
            .order_by(desc(TeacherQuizGenerationRun.created_at))
            .first()
        )

    def create_generation_run(self, run: TeacherQuizGenerationRun) -> TeacherQuizGenerationRun:
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    # ---------------------------------------------------------------------
    # Duplicate
    # ---------------------------------------------------------------------

    def duplicate_quiz(
        self,
        *,
        source: TeacherQuiz,
        new_id: UUID,
        new_title: str,
        now: datetime,
    ) -> TeacherQuiz:
        copy = TeacherQuiz(
            id=new_id,
            tenant_id=source.tenant_id,
            owner_user_id=source.owner_user_id,
            title=new_title,
            subject=source.subject,
            grade=source.grade,
            student_instructions=source.student_instructions,
            teacher_notes=source.teacher_notes,
            time_limit_minutes=source.time_limit_minutes,
            status="draft" if source.status == "archived" else source.status,
            assigned_at=None,
            due_at=None,
            source_pack_ids=list(source.source_pack_ids or []),
            scope_topics=list(source.scope_topics or []),
            scope_refinement=source.scope_refinement,
            topic_summary=source.topic_summary,
            generate_without_sources=bool(source.generate_without_sources),
            difficulty=source.difficulty,
            shuffle_questions=bool(source.shuffle_questions),
            shuffle_answers=bool(source.shuffle_answers),
            negative_marking=bool(source.negative_marking),
            handout_layout=source.handout_layout,
            class_keys=list(source.class_keys or []),
            questions_count=source.questions_count,
            total_marks=source.total_marks,
            submission_count=0,
            avg_score=0.0,
            content_version=1,
            created_at=now,
            updated_at=now,
        )

        # Copy question rows (preserve order)
        for q in (source.questions or []):
            copy.questions.append(
                TeacherQuizQuestion(
                    sort_order=q.sort_order,
                    type=q.type,
                    prompt=q.prompt,
                    points=q.points,
                    options=q.options,
                    response_lines=q.response_lines,
                    extra=q.extra,
                )
            )

        self.db.add(copy)
        self.db.commit()
        self.db.refresh(copy)
        return copy

