"""
数据库模型 — Learning Tracker
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Text, Boolean, DateTime, Date, ForeignKey, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.learning_tracker.core.database import Base


class LearningDay(Base):
    __tablename__ = "learning_days"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    week_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[datetime] = mapped_column(Date, nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    subtitle: Mapped[str] = mapped_column(String(300), nullable=True)
    tasks: Mapped[list] = mapped_column(JSON, nullable=False)
    objectives: Mapped[str] = mapped_column(Text, nullable=True)
    git_filter: Mapped[str] = mapped_column(String(500), nullable=True)
    is_rest_day: Mapped[bool] = mapped_column(Boolean, default=False)

    checkin: Mapped["CheckIn"] = relationship("CheckIn", back_populates="learning_day", uselist=False)
    question: Mapped["DailyQuestion"] = relationship("DailyQuestion", back_populates="learning_day", uselist=False)

    __table_args__ = (
        Index("ix_learning_days_week_day", "week_number", "day_number"),
    )


class CheckIn(Base):
    __tablename__ = "checkins"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    day_id: Mapped[str] = mapped_column(String(36), ForeignKey("learning_days.id"), nullable=False)
    checked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    mood: Mapped[str] = mapped_column(String(50), nullable=True)
    note: Mapped[str] = mapped_column(Text, nullable=True)
    completed_tasks: Mapped[list] = mapped_column(JSON, nullable=True)
    uncompleted_tasks: Mapped[list] = mapped_column(JSON, nullable=True)
    git_commits: Mapped[list] = mapped_column(JSON, nullable=True)

    learning_day: Mapped["LearningDay"] = relationship("LearningDay", back_populates="checkin")


class DailyQuestion(Base):
    __tablename__ = "daily_questions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    day_id: Mapped[str] = mapped_column(String(36), ForeignKey("learning_days.id"), nullable=False, unique=True)
    question_type: Mapped[str] = mapped_column(String(20), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[list] = mapped_column(JSON, nullable=True)
    correct_answer: Mapped[str] = mapped_column(String(500), nullable=True)
    explanation: Mapped[str] = mapped_column(Text, nullable=True)
    difficulty: Mapped[int] = mapped_column(Integer, default=1)

    learning_day: Mapped["LearningDay"] = relationship("LearningDay", back_populates="question")


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question_id: Mapped[str] = mapped_column(String(36), ForeignKey("daily_questions.id"), nullable=False)
    user_answer: Mapped[str] = mapped_column(String(500), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    answer_text: Mapped[str] = mapped_column(Text, nullable=True)
