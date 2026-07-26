"""Contact form router."""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ContactMessage
from app.auth.security import get_current_user

router = APIRouter(tags=["contact"])
templates = Jinja2Templates(directory="app/templates")


@router.post("/contact")
def submit_contact(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db),
):
    msg = ContactMessage(name=name, email=email, message=message)
    db.add(msg)
    db.commit()
    return RedirectResponse(url="/?contacted=1#contact", status_code=302)
