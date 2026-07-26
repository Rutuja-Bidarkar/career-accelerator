"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr


# ---------------------------------------------------------------------------
# Auth schemas
# ---------------------------------------------------------------------------

class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Contact
# ---------------------------------------------------------------------------

class ContactForm(BaseModel):
    name: str
    email: str
    message: str


# ---------------------------------------------------------------------------
# Roadmap Progress
# ---------------------------------------------------------------------------

class RoadmapToggle(BaseModel):
    roadmap_type: str   # "career" or "no_degree"
    roadmap_id: int
    step_id: int
    completed: bool


# ---------------------------------------------------------------------------
# Psychometric
# ---------------------------------------------------------------------------

class PsychometricSubmit(BaseModel):
    answers: Dict[str, int]  # {str(question_id): 1-5}


# ---------------------------------------------------------------------------
# Interview
# ---------------------------------------------------------------------------

class InterviewStart(BaseModel):
    job_role: str


class InterviewAnswer(BaseModel):
    session_id: str
    answer: str


class InterviewEnd(BaseModel):
    session_id: str


# ---------------------------------------------------------------------------
# Resume
# ---------------------------------------------------------------------------

class ResumeAnalysisOut(BaseModel):
    id: int
    filename: Optional[str]
    uploaded_at: datetime
    overall_score: Optional[int]
    strengths: Optional[List[str]]
    weaknesses: Optional[List[str]]
    existing_skills: Optional[List[str]]
    missing_skills: Optional[List[str]]
    suggested_courses: Optional[List[str]]

    class Config:
        from_attributes = True
