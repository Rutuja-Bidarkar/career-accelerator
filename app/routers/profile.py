"""Profile router: dashboard with history."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    User, UserRoadmapProgress, RoadmapType, Career, NoDegree,
    PsychometricResult, ResumeAnalysis, InterviewSession
)
from app.auth.security import require_current_user

router = APIRouter(tags=["profile"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request, db: Session = Depends(get_db)):
    try:
        current_user = require_current_user(request, db)
    except Exception as e:
        return RedirectResponse(url="/login?next=/profile", status_code=302)

    # 1. Roadmap Progress Overview
    progress_rows = db.query(UserRoadmapProgress).filter(
        UserRoadmapProgress.user_id == current_user.id
    ).all()
    
    # Aggregate progress by roadmap type and ID
    progress_map = {}
    for r in progress_rows:
        key = (r.roadmap_type, r.roadmap_id)
        if key not in progress_map:
            progress_map[key] = {"completed": 0, "title": "", "slug": "", "type": r.roadmap_type}
        if r.completed:
            progress_map[key]["completed"] += 1

    # Enrich with titles and total steps
    for key, data in progress_map.items():
        rtype, rid = key
        if rtype == RoadmapType.career:
            c = db.query(Career).get(rid)
            if c:
                data["title"] = c.name
                data["slug"] = f"/services/careers/{c.slug}"
                data["total"] = len(c.roadmap_steps)
        elif rtype == RoadmapType.no_degree:
            n = db.query(NoDegree).get(rid)
            if n:
                data["title"] = n.name
                data["slug"] = f"/services/no-degree/{n.slug}"
                data["total"] = len(n.roadmap_steps)
                
    active_roadmaps = [v for v in progress_map.values() if v.get("total", 0) > 0]
    for ar in active_roadmaps:
        ar["pct"] = int((ar["completed"] / ar["total"]) * 100)

    # 2. Resume Reports
    resumes = db.query(ResumeAnalysis).filter(
        ResumeAnalysis.user_id == current_user.id
    ).order_by(ResumeAnalysis.uploaded_at.desc()).all()

    # 3. Interview History
    interviews = db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id
    ).order_by(InterviewSession.started_at.desc()).all()

    # 4. Psychometric Result (latest)
    psycho = db.query(PsychometricResult).filter(
        PsychometricResult.user_id == current_user.id
    ).order_by(PsychometricResult.taken_at.desc()).first()

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "current_user": current_user,
        "active_roadmaps": active_roadmaps,
        "resumes": resumes,
        "interviews": interviews,
        "psycho": psycho,
    })
