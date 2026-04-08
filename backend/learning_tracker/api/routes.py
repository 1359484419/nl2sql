"""
API 路由 — Learning Tracker
"""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.learning_tracker.core.database import get_db
from backend.learning_tracker.models.models import LearningDay, CheckIn, DailyQuestion, Answer
from backend.learning_tracker.api.schemas import (
    CheckInRequest, CheckInResponse, GitCommit,
    DailyQuestionResponse, AnswerSubmitRequest, AnswerResponse,
    LearningDayResponse, WeekSummaryResponse,
)
from backend.learning_tracker.services.git_service import GitService

router = APIRouter(prefix="/learning", tags=["Learning Tracker"])


async def _day_to_response(day: LearningDay, db: AsyncSession) -> LearningDayResponse:
    is_checked_in = day.checkin is not None
    if day.checkin is None:
        r = await db.execute(select(CheckIn).where(CheckIn.day_id == day.id))
        checkin = r.scalar_one_or_none()
    else:
        checkin = day.checkin
    question_resp = None
    if day.question:
        question_resp = DailyQuestionResponse(
            id=day.question.id,
            day_id=day.question.day_id,
            question_type=day.question.question_type,
            question_text=day.question.question_text,
            options=day.question.options,
            difficulty=day.question.difficulty,
        )
    checkin_resp = None
    if checkin:
        checkin_resp = CheckInResponse(
            id=checkin.id,
            day_id=checkin.day_id,
            checked_at=checkin.checked_at,
            mood=checkin.mood,
            note=checkin.note,
            completed_tasks=checkin.completed_tasks or [],
            uncompleted_tasks=checkin.uncompleted_tasks or [],
            git_commits=[GitCommit(**c) for c in (checkin.git_commits or [])],
        )
    return LearningDayResponse(
        id=day.id,
        week_number=day.week_number,
        day_number=day.day_number,
        date=day.date,
        title=day.title,
        subtitle=day.subtitle,
        tasks=day.tasks or [],
        objectives=day.objectives,
        is_rest_day=day.is_rest_day,
        is_checked_in=is_checked_in,
        question=question_resp,
        checkin=checkin_resp,
    )


@router.post("/checkin", response_model=CheckInResponse)
async def create_checkin(req: CheckInRequest, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(CheckIn).where(CheckIn.day_id == req.day_id))
    existing = r.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="今日已打卡")
    rd = await db.execute(select(LearningDay).where(LearningDay.id == req.day_id))
    if not rd.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="学习日不存在")
    git_service = GitService()
    day_date = (await db.execute(select(LearningDay.date).where(LearningDay.id == req.day_id))).scalar_one_or_none()
    commits = []
    if day_date:
        commits = git_service.get_commits_by_date(str(day_date))
    checkin = CheckIn(
        day_id=req.day_id,
        mood=req.mood,
        note=req.note,
        completed_tasks=req.completed_tasks,
        uncompleted_tasks=req.uncompleted_tasks,
        git_commits=[{"hash": c["hash"], "message": c["message"], "author": c["author"], "date": c["date"]} for c in commits],
    )
    db.add(checkin)
    await db.commit()
    await db.refresh(checkin)
    return CheckInResponse(
        id=checkin.id,
        day_id=checkin.day_id,
        checked_at=checkin.checked_at,
        mood=checkin.mood,
        note=checkin.note,
        completed_tasks=checkin.completed_tasks or [],
        uncompleted_tasks=checkin.uncompleted_tasks or [],
        git_commits=[GitCommit(**c) for c in (checkin.git_commits or [])],
    )


@router.get("/checkin/{day_id}", response_model=Optional[CheckInResponse])
async def get_checkin(day_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(CheckIn).where(CheckIn.day_id == day_id))
    checkin = r.scalar_one_or_none()
    if not checkin:
        return None
    return CheckInResponse(
        id=checkin.id,
        day_id=checkin.day_id,
        checked_at=checkin.checked_at,
        mood=checkin.mood,
        note=checkin.note,
        completed_tasks=checkin.completed_tasks or [],
        uncompleted_tasks=checkin.uncompleted_tasks or [],
        git_commits=[GitCommit(**c) for c in (checkin.git_commits or [])],
    )


@router.get("/question/{day_id}", response_model=Optional[DailyQuestionResponse])
async def get_question(day_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(DailyQuestion).where(DailyQuestion.day_id == day_id))
    q = r.scalar_one_or_none()
    if not q:
        return None
    return DailyQuestionResponse(
        id=q.id, day_id=q.day_id, question_type=q.question_type,
        question_text=q.question_text, options=q.options, difficulty=q.difficulty,
    )


@router.post("/answer", response_model=AnswerResponse)
async def submit_answer(req: AnswerSubmitRequest, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(DailyQuestion).where(DailyQuestion.id == req.question_id))
    question = r.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    is_correct = None
    if question.question_type != "concept":
        user = req.user_answer.strip().upper().replace(" ", "")
        correct = (question.correct_answer or "").strip().upper().replace(" ", "")
        if question.question_type == "multiple":
            user_set = set(user.split(","))
            correct_set = set(correct.split(","))
            is_correct = user_set == correct_set
        else:
            is_correct = user == correct
    answer = Answer(
        question_id=req.question_id,
        user_answer=req.user_answer,
        is_correct=is_correct,
        answer_text=req.answer_text,
    )
    db.add(answer)
    await db.commit()
    await db.refresh(answer)
    return AnswerResponse(
        id=answer.id,
        question_id=answer.question_id,
        user_answer=answer.user_answer,
        is_correct=answer.is_correct,
        correct_answer=question.correct_answer if question.question_type != "concept" else None,
        explanation=question.explanation,
        submitted_at=answer.submitted_at,
    )


@router.get("/day/{day_id}", response_model=LearningDayResponse)
async def get_learning_day(day_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(
        select(LearningDay)
        .options(selectinload(LearningDay.checkin), selectinload(LearningDay.question))
        .where(LearningDay.id == day_id)
    )
    day = r.scalar_one_or_none()
    if not day:
        raise HTTPException(status_code=404, detail="学习日不存在")
    return await _day_to_response(day, db)


@router.get("/day/by-date/{date_str}", response_model=Optional[LearningDayResponse])
async def get_day_by_date(date_str: str, db: AsyncSession = Depends(get_db)):
    from datetime import date as date_cls
    parsed = date_cls.fromisoformat(date_str)
    r = await db.execute(
        select(LearningDay)
        .options(selectinload(LearningDay.checkin), selectinload(LearningDay.question))
        .where(LearningDay.date == parsed)
    )
    day = r.scalar_one_or_none()
    if not day:
        return None
    return await _day_to_response(day, db)


@router.get("/week/{week_number}", response_model=WeekSummaryResponse)
async def get_week_summary(week_number: int, db: AsyncSession = Depends(get_db)):
    r = await db.execute(
        select(LearningDay)
        .options(selectinload(LearningDay.checkin), selectinload(LearningDay.question))
        .where(LearningDay.week_number == week_number)
        .order_by(LearningDay.day_number)
    )
    days = list(r.scalars().all())
    if not days:
        raise HTTPException(status_code=404, detail="该周不存在")
    total_days = len(days)
    checked_in_days = sum(1 for d in days if d.checkin is not None)
    questions_total = sum(1 for d in days if d.question is not None)
    questions_answered = 0
    questions_correct = 0
    for d in days:
        if d.question:
            ra = await db.execute(select(Answer).where(Answer.question_id == d.question.id))
            answers = list(ra.scalars().all())
            if answers:
                questions_answered += 1
                questions_correct += sum(1 for a in answers if a.is_correct)
    return WeekSummaryResponse(
        week_number=week_number,
        days=[await _day_to_response(d, db) for d in days],
        total_days=total_days,
        checked_in_days=checked_in_days,
        completion_rate=round(checked_in_days / total_days * 100, 1) if total_days else 0,
        questions_total=questions_total,
        questions_answered=questions_answered,
        questions_correct=questions_correct,
    )


@router.get("/all-days", response_model=list[LearningDayResponse])
async def get_all_days(db: AsyncSession = Depends(get_db)):
    r = await db.execute(
        select(LearningDay)
        .options(selectinload(LearningDay.checkin), selectinload(LearningDay.question))
        .order_by(LearningDay.date)
    )
    days = list(r.scalars().all())
    return [await _day_to_response(d, db) for d in days]


@router.get("/today", response_model=Optional[LearningDayResponse])
async def get_today(db: AsyncSession = Depends(get_db)):
    today_str = date.today().isoformat()
    return await get_day_by_date(today_str, db)


@router.get("/git/commits")
async def get_git_commits(
    since: Optional[str] = None,
    until: Optional[str] = None,
    keyword: Optional[str] = None,
    limit: int = 50,
):
    service = GitService()
    commits = service.get_commits(since=since, until=until, keyword=keyword, limit=limit)
    return {"commits": commits}


@router.get("/git/weekly-stats")
async def get_weekly_stats():
    service = GitService()
    return service.get_weekly_stats()
