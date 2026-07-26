"""Startup roadmap router."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import StartupRoadmapStep, UserStartupProgress
from app.auth.security import get_current_user

router = APIRouter(tags=["startup"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/services/startup", response_class=HTMLResponse)
def startup_roadmap(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user:
        return RedirectResponse(url="/login?next=/services/startup", status_code=302)

    steps = db.query(StartupRoadmapStep).order_by(StartupRoadmapStep.step_order).all()
    completed_steps = set()
    if current_user:
        rows = db.query(UserStartupProgress).filter(
            UserStartupProgress.user_id == current_user.id,
            UserStartupProgress.completed == True,
        ).all()
        completed_steps = {row.step_id for row in rows}

    return templates.TemplateResponse("startup.html", {
        "request": request,
        "steps": steps,
        "completed_steps": completed_steps,
        "current_user": current_user,
    })
