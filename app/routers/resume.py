"""Resume Analyzer Router"""

from fastapi import APIRouter, Depends, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.security import get_current_user, require_current_user
from app.agents.resume_agent import run_resume_pipeline
from app.models import ResumeAnalysis

router = APIRouter(tags=["resume"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/services/resume", response_class=HTMLResponse)
def resume_page(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login?next=/services/resume", status_code=302)
    return templates.TemplateResponse("resume_analyzer.html", {
        "request": request,
        "current_user": current_user,
    })

@router.post("/services/resume")
async def analyze_resume(
    request: Request,
    file: UploadFile = File(...),
    job_description: str = Form(""),
    db: Session = Depends(get_db)
):
    current_user = require_current_user(request, db)
    
    # Read file bytes
    file_bytes = await file.read()
    
    # Run pipeline
    analysis_id = run_resume_pipeline(db, current_user.id, file_bytes, file.filename, job_description)
    
    # Fetch result
    analysis = db.query(ResumeAnalysis).get(analysis_id)
    
    return JSONResponse({
        "success": True,
        "overall_score": analysis.overall_score,
        "strengths": analysis.strengths,
        "weaknesses": analysis.weaknesses,
        "existing_skills": analysis.existing_skills,
        "missing_skills": analysis.missing_skills,
        "suggested_courses": analysis.suggested_courses
    })
