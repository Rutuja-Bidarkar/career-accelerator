"""Mock Interview Router"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.auth.security import get_current_user, require_current_user
from app.models import InterviewSession as DBInterviewSession
from app.schemas import InterviewStart, InterviewAnswer, InterviewEnd
from app.agents.interview_agent import (
    create_interview_session,
    get_next_question,
    process_answer,
    end_interview_session,
    pop_session
)

router = APIRouter(tags=["interview"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/services/interview", response_class=HTMLResponse)
def interview_page(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login?next=/services/interview", status_code=302)
    return templates.TemplateResponse("mock_interview.html", {
        "request": request,
        "current_user": current_user,
    })

@router.post("/api/interview/start")
async def api_start_interview(data: InterviewStart, request: Request, db: Session = Depends(get_db)):
    require_current_user(request, db)
    session_id = create_interview_session(data.job_role)
    first_q = get_next_question(session_id)
    return JSONResponse({"session_id": session_id, "question": first_q})

@router.post("/api/interview/answer")
async def api_answer_interview(data: InterviewAnswer, request: Request, db: Session = Depends(get_db)):
    require_current_user(request, db)
    next_q = process_answer(data.session_id, data.answer)
    return JSONResponse({"question": next_q})

@router.post("/api/interview/end")
async def api_end_interview(data: InterviewEnd, request: Request, db: Session = Depends(get_db)):
    current_user = require_current_user(request, db)
    
    # Run evaluation
    results = end_interview_session(data.session_id)
    
    # Save to DB and pop from memory
    session_data = pop_session(data.session_id)
    if session_data:
        db_session = DBInterviewSession(
            user_id=current_user.id,
            job_role=results["job_role"],
            ended_at=datetime.utcnow(),
            transcript=results["transcript"],
            performance_summary=results["summary"],
            score=results["score"]
        )
        db.add(db_session)
        db.commit()
        
    return JSONResponse(results)
