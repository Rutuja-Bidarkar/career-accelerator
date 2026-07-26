"""
SQLAlchemy ORM models for Career Accelerator.
Designed for SQLite (dev) and PostgreSQL (prod) compatibility.
"""

import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime,
    ForeignKey, Enum as SAEnum, JSON
)
from sqlalchemy.orm import relationship
from app.database import Base


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class RoadmapType(str, enum.Enum):
    career = "career"
    no_degree = "no_degree"


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    roadmap_progress = relationship("UserRoadmapProgress", back_populates="user")
    psychometric_results = relationship("PsychometricResult", back_populates="user")
    resume_analyses = relationship("ResumeAnalysis", back_populates="user")
    interview_sessions = relationship("InterviewSession", back_populates="user")
    startup_progress = relationship("UserStartupProgress", back_populates="user")


# ---------------------------------------------------------------------------
# Career Categories & Careers
# ---------------------------------------------------------------------------

class CareerCategory(Base):
    __tablename__ = "career_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    icon = Column(String(10), nullable=True)

    careers = relationship("Career", back_populates="category")


class Career(Base):
    __tablename__ = "careers"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("career_categories.id"), nullable=False)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    overview = Column(Text, nullable=True)
    skills_required = Column(Text, nullable=True)
    learning_resources = Column(JSON, nullable=True)  # [{title, url}]
    job_roles = Column(Text, nullable=True)
    salary_range = Column(String(100), nullable=True)
    future_scope = Column(Text, nullable=True)
    success_story = Column(Text, nullable=True)
    video_url = Column(String(255), nullable=True)
    scholarships = Column(JSON, nullable=True)  # [{name, url, eligibility, last_verified}]

    category = relationship("CareerCategory", back_populates="careers")
    roadmap_steps = relationship("CareerRoadmapStep", back_populates="career", order_by="CareerRoadmapStep.step_order")


class CareerRoadmapStep(Base):
    __tablename__ = "career_roadmap_steps"

    id = Column(Integer, primary_key=True, index=True)
    career_id = Column(Integer, ForeignKey("careers.id"), nullable=False)
    step_order = Column(Integer, nullable=False)
    title = Column(Text, nullable=False)

    career = relationship("Career", back_populates="roadmap_steps")


# ---------------------------------------------------------------------------
# No-Degree Paths
# ---------------------------------------------------------------------------

class NoDegree(Base):
    __tablename__ = "no_degree_paths"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False, default="Freelancing")
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    icon = Column(String(10), nullable=True)
    skills_required = Column(Text, nullable=True)
    learning_resources = Column(JSON, nullable=True)
    income_salary = Column(String(100), nullable=True)
    where_to_find_work = Column(Text, nullable=True)
    success_story = Column(Text, nullable=True)

    roadmap_steps = relationship("NoDegreeRoadmapStep", back_populates="path", order_by="NoDegreeRoadmapStep.step_order")


class NoDegreeRoadmapStep(Base):
    __tablename__ = "no_degree_roadmap_steps"

    id = Column(Integer, primary_key=True, index=True)
    path_id = Column(Integer, ForeignKey("no_degree_paths.id"), nullable=False)
    step_order = Column(Integer, nullable=False)
    title = Column(Text, nullable=False)
    detail = Column(Text, nullable=True)

    path = relationship("NoDegree", back_populates="roadmap_steps")


# ---------------------------------------------------------------------------
# User Roadmap Progress
# ---------------------------------------------------------------------------

class UserRoadmapProgress(Base):
    __tablename__ = "user_roadmap_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    roadmap_type = Column(SAEnum(RoadmapType), nullable=False)
    roadmap_id = Column(Integer, nullable=False)   # career.id or no_degree_path.id
    step_id = Column(Integer, nullable=False)       # career_roadmap_step.id or no_degree_roadmap_step.id
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="roadmap_progress")


# ---------------------------------------------------------------------------
# Psychometric Assessment
# ---------------------------------------------------------------------------

class PsychometricQuestion(Base):
    __tablename__ = "psychometric_questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    trait_tag = Column(String(50), nullable=False)  # analytical/creative/social/technical


class PsychometricResult(Base):
    __tablename__ = "psychometric_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    taken_at = Column(DateTime, default=datetime.utcnow)
    answers = Column(JSON, nullable=True)              # {question_id: true/false}
    trait_scores = Column(JSON, nullable=True)         # {trait: score}
    recommended_categories = Column(JSON, nullable=True)
    recommended_careers = Column(JSON, nullable=True)
    ai_summary = Column(Text, nullable=True)

    user = relationship("User", back_populates="psychometric_results")


# ---------------------------------------------------------------------------
# Resume Analysis
# ---------------------------------------------------------------------------

class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    target_job_description = Column(Text, nullable=True)
    overall_score = Column(Integer, nullable=True)
    strengths = Column(JSON, nullable=True)
    weaknesses = Column(JSON, nullable=True)
    existing_skills = Column(JSON, nullable=True)
    missing_skills = Column(JSON, nullable=True)
    suggested_courses = Column(JSON, nullable=True)
    raw_ai_output = Column(Text, nullable=True)

    user = relationship("User", back_populates="resume_analyses")


# ---------------------------------------------------------------------------
# Mock Interview
# ---------------------------------------------------------------------------

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_role = Column(String(100), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    transcript = Column(JSON, nullable=True)           # [{role, message, timestamp}]
    performance_summary = Column(Text, nullable=True)
    score = Column(Integer, nullable=True)

    user = relationship("User", back_populates="interview_sessions")


# ---------------------------------------------------------------------------
# Startup Roadmap
# ---------------------------------------------------------------------------

class StartupRoadmapStep(Base):
    __tablename__ = "startup_roadmap_steps"

    id = Column(Integer, primary_key=True, index=True)
    step_order = Column(Integer, nullable=False)
    title = Column(String(100), nullable=False)
    detail = Column(Text, nullable=True)
    what_to_do = Column(JSON, nullable=True)
    why_it_matters = Column(Text, nullable=True)
    tool_template = Column(Text, nullable=True)
    done_when = Column(Text, nullable=True)

    user_progress = relationship("UserStartupProgress", back_populates="step")


class UserStartupProgress(Base):
    __tablename__ = "user_startup_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    step_id = Column(Integer, ForeignKey("startup_roadmap_steps.id"), nullable=False)
    completed = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)

    user = relationship("User", back_populates="startup_progress")
    step = relationship("StartupRoadmapStep", back_populates="user_progress")


# ---------------------------------------------------------------------------
# Contact Messages
# ---------------------------------------------------------------------------

class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)
