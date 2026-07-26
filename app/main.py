from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.database import engine, Base
from app.auth.routes import router as auth_router
from app.routers.careers import router as careers_router
from app.routers.no_degree import router as no_degree_router
from app.routers.startup import router as startup_router
from app.routers.contact import router as contact_router
from app.routers.profile import router as profile_router
from app.routers.psychometric import router as psychometric_router
from app.routers.resume import router as resume_router
from app.routers.interview import router as interview_router

from app.auth.security import get_current_user
from sqlalchemy.orm import Session
from app.database import SessionLocal

# Create DB tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Career Accelerator")

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Include Routers
app.include_router(auth_router)
app.include_router(careers_router)
app.include_router(no_degree_router)
app.include_router(startup_router)
app.include_router(contact_router)
app.include_router(profile_router)
app.include_router(psychometric_router)
app.include_router(resume_router)
app.include_router(interview_router)

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    db = SessionLocal()
    current_user = get_current_user(request, db)
    db.close()
    if not current_user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "current_user": current_user
    })
