"""
API 请求 / 响应模型
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class CheckInRequest(BaseModel):
    day_id: str
    mood: Optional[str] = None
    note: Optional[str] = None
    completed_tasks: list[str] = []
    uncompleted_tasks: list[str] = []


class GitCommit(BaseModel):
    hash: str
    message: str
    author: str
    date: str


class CheckInResponse(BaseModel):
    id: str
    day_id: str
    checked_at: datetime
    mood: Optional[str]
    note: Optional[str]
    completed_tasks: list[str]
    uncompleted_tasks: list[str]
    git_commits: list[GitCommit]

    class Config:
        from_attributes = True


class OptionItem(BaseModel):
    label: str
    text: str


class DailyQuestionResponse(BaseModel):
    id: str
    day_id: str
    question_type: str
    question_text: str
    options: Optional[list[OptionItem]]
    difficulty: int

    class Config:
        from_attributes = True


class AnswerSubmitRequest(BaseModel):
    question_id: str
    user_answer: str
    answer_text: Optional[str] = None


class AnswerResponse(BaseModel):
    id: str
    question_id: str
    user_answer: str
    is_correct: Optional[bool]
    correct_answer: Optional[str]
    explanation: Optional[str]
    submitted_at: datetime

    class Config:
        from_attributes = True


class LearningDayResponse(BaseModel):
    id: str
    week_number: int
    day_number: int
    date: date
    title: str
    subtitle: Optional[str]
    tasks: list[str]
    objectives: Optional[str]
    is_rest_day: bool
    is_checked_in: bool
    question: Optional[DailyQuestionResponse]
    checkin: Optional[CheckInResponse]

    class Config:
        from_attributes = True


class WeekSummaryResponse(BaseModel):
    week_number: int
    days: list[LearningDayResponse]
    total_days: int
    checked_in_days: int
    completion_rate: float
    questions_total: int
    questions_answered: int
    questions_correct: int
