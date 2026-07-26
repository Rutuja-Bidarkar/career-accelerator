# Career Accelerator

A complete, production-quality AI career guidance platform built with FastAPI, SQLite, and vanilla HTML/JS/CSS.

## Features
- JWT Authentication
- Psychometric Assessments (AI-scored)
- Resume Analyzer (PDF/DOCX extraction & AI evaluation)
- Mock Interview Bot (Stateful chat interface)
- Career & No-Degree Roadmaps with live progress tracking
- Complete pixel-accurate landing page

## Setup Instructions

1. **Environment Variables**:
   Copy `.env.example` to `.env` and add your Groq API Key.
   ```bash
   cp .env.example .env
   # Edit .env and set GROQ_API_KEY
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize Database & Seed Data**:
   This creates the SQLite database and populates it with categories, careers, and questions.
   ```bash
   python seed_data/seed.py
   ```

4. **Run the Application**:
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access**:
   Navigate to `http://localhost:8000` in your browser.
