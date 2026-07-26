"""No-degree paths router."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import NoDegree, NoDegreeRoadmapStep, UserRoadmapProgress, RoadmapType
from app.auth.security import get_current_user

router = APIRouter(tags=["no_degree"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/services/no-degree", response_class=HTMLResponse)
def no_degree_grid(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    paths = db.query(NoDegree).all()
    
    # Group by category
    grouped_paths = {}
    for p in paths:
        if p.category not in grouped_paths:
            grouped_paths[p.category] = []
        grouped_paths[p.category].append(p)
        
    # Standardize the order based on requested categories
    ordered_categories = [
        "Freelancing",
        "Part-time Jobs",
        "Quick Income Ideas",
        "Entrepreneurial Ventures",
        "Creative & Craft-Based Jobs",
        "Side Hustles",
        "Government Skill Programs"
    ]
    
    ordered_grouped_paths = {cat: grouped_paths.get(cat, []) for cat in ordered_categories if cat in grouped_paths}
    
    return templates.TemplateResponse("no_degree_grid.html", {
        "request": request,
        "grouped_paths": ordered_grouped_paths,
        "current_user": current_user,
    })


@router.get("/services/no-degree/{slug}", response_class=HTMLResponse)
def no_degree_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    path = db.query(NoDegree).filter(NoDegree.slug == slug).first()
    if not path:
        raise HTTPException(status_code=404, detail="Path not found")

    steps = db.query(NoDegreeRoadmapStep).filter(
        NoDegreeRoadmapStep.path_id == path.id
    ).order_by(NoDegreeRoadmapStep.step_order).all()

    completed_steps = set()
    progress_pct = 0
    if current_user and steps:
        progress_rows = db.query(UserRoadmapProgress).filter(
            UserRoadmapProgress.user_id == current_user.id,
            UserRoadmapProgress.roadmap_type == RoadmapType.no_degree,
            UserRoadmapProgress.roadmap_id == path.id,
            UserRoadmapProgress.completed == True,
        ).all()
        completed_steps = {row.step_id for row in progress_rows}
        progress_pct = int(len(completed_steps) / len(steps) * 100) if steps else 0

    return templates.TemplateResponse("no_degree_detail.html", {
        "request": request,
        "path": path,
        "steps": steps,
        "completed_steps": completed_steps,
        "progress_pct": progress_pct,
        "current_user": current_user,
    })
