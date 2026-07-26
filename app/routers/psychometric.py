"""Psychometric assessment router."""

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PsychometricQuestion, PsychometricResult, CareerCategory, Career
from app.auth.security import get_current_user, require_current_user
from app.schemas import PsychometricSubmit
from app.agents.psychometric_agent import run_psychometric_pipeline

router = APIRouter(tags=["psychometric"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/services/psychometric", response_class=HTMLResponse)
def psychometric_page(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user:
        return RedirectResponse(url="/login?next=/services/psychometric", status_code=302)
        
    questions = db.query(PsychometricQuestion).all()
    return templates.TemplateResponse("psychometric.html", {
        "request": request,
        "questions": questions,
        "current_user": current_user,
    })


@router.post("/services/psychometric")
async def psychometric_submit(request: Request, data: PsychometricSubmit, db: Session = Depends(get_db)):
    current_user = require_current_user(request, db)
    
    # Run pipeline
    result_id = run_psychometric_pipeline(db, current_user.id, data.answers)
    
    return JSONResponse({"success": True, "redirect_url": f"/services/psychometric/results/{result_id}"})


@router.get("/services/psychometric/results/{result_id}", response_class=HTMLResponse)
def psychometric_results_page(result_id: int, request: Request, db: Session = Depends(get_db)):
    current_user = require_current_user(request, db)
    
    result = db.query(PsychometricResult).filter(
        PsychometricResult.id == result_id,
        PsychometricResult.user_id == current_user.id
    ).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
        
    # The new recommended_careers is stored directly as a JSON object (list of dicts)
    recommended_careers = result.recommended_careers or []
            
    return templates.TemplateResponse("psychometric_results.html", {
        "request": request,
        "result": result,
        "recommended_careers": recommended_careers,
        "current_user": current_user,
    })
