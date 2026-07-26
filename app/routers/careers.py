"""Careers router: grid and detail pages."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Career, CareerCategory, CareerRoadmapStep,
    UserRoadmapProgress, RoadmapType
)
from app.auth.security import get_current_user

router = APIRouter(tags=["careers"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/services/careers", response_class=HTMLResponse)
def careers_grid(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    categories = db.query(CareerCategory).all()
    # Eager-load careers for each category
    for cat in categories:
        cat.careers  # trigger lazy load
    return templates.TemplateResponse("careers_grid.html", {
        "request": request,
        "categories": categories,
        "current_user": current_user,
    })


@router.get("/services/careers/{slug}", response_class=HTMLResponse)
def career_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    career = db.query(Career).filter(Career.slug == slug).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found")

    # Load roadmap steps
    steps = db.query(CareerRoadmapStep).filter(
        CareerRoadmapStep.career_id == career.id
    ).order_by(CareerRoadmapStep.step_order).all()

    # Compute progress
    completed_steps = set()
    progress_pct = 0
    if current_user and steps:
        progress_rows = db.query(UserRoadmapProgress).filter(
            UserRoadmapProgress.user_id == current_user.id,
            UserRoadmapProgress.roadmap_type == RoadmapType.career,
            UserRoadmapProgress.roadmap_id == career.id,
            UserRoadmapProgress.completed == True,
        ).all()
        completed_steps = {row.step_id for row in progress_rows}
        progress_pct = int(len(completed_steps) / len(steps) * 100) if steps else 0

    return templates.TemplateResponse("career_detail.html", {
        "request": request,
        "career": career,
        "steps": steps,
        "completed_steps": completed_steps,
        "progress_pct": progress_pct,
        "current_user": current_user,
    })


@router.post("/api/roadmap/toggle")
async def toggle_roadmap_step(request: Request, db: Session = Depends(get_db)):
    """AJAX endpoint: toggle a roadmap step's completion."""
    current_user = get_current_user(request, db)
    if not current_user:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    data = await request.json()
    roadmap_type_str = data.get("roadmap_type")
    roadmap_id = data.get("roadmap_id")
    step_id = data.get("step_id")
    completed = data.get("completed", True)

    try:
        roadmap_type = RoadmapType(roadmap_type_str)
    except ValueError:
        return JSONResponse({"error": "Invalid roadmap_type"}, status_code=400)

    from datetime import datetime
    # Upsert
    row = db.query(UserRoadmapProgress).filter(
        UserRoadmapProgress.user_id == current_user.id,
        UserRoadmapProgress.roadmap_type == roadmap_type,
        UserRoadmapProgress.roadmap_id == roadmap_id,
        UserRoadmapProgress.step_id == step_id,
    ).first()

    if row:
        row.completed = completed
        row.completed_at = datetime.utcnow() if completed else None
    else:
        row = UserRoadmapProgress(
            user_id=current_user.id,
            roadmap_type=roadmap_type,
            roadmap_id=roadmap_id,
            step_id=step_id,
            completed=completed,
            completed_at=datetime.utcnow() if completed else None,
        )
        db.add(row)
    db.commit()

    # Return new progress percentage
    total_steps = data.get("total_steps", 1)
    completed_count = db.query(UserRoadmapProgress).filter(
        UserRoadmapProgress.user_id == current_user.id,
        UserRoadmapProgress.roadmap_type == roadmap_type,
        UserRoadmapProgress.roadmap_id == roadmap_id,
        UserRoadmapProgress.completed == True,
    ).count()
    pct = int(completed_count / total_steps * 100) if total_steps else 0
    return JSONResponse({"success": True, "progress_pct": pct, "completed_count": completed_count})
