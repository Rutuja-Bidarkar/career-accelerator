import io
import json
import pdfplumber
import docx
from sqlalchemy.orm import Session
from app.models import ResumeAnalysis
from app.agents.llm_client import chat_completion

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    ext = filename.split('.')[-1].lower()
    text = ""
    try:
        if ext == 'pdf':
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
        elif ext in ['docx', 'doc']:
            doc = docx.Document(io.BytesIO(file_bytes))
            for para in doc.paragraphs:
                text += para.text + "\n"
        else:
            # Fallback to plain text decode
            text = file_bytes.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Extraction error: {e}")
        text = "Failed to extract text."
    return text.strip()

def run_resume_pipeline(db: Session, user_id: int, file_bytes: bytes, filename: str, jd: str = "") -> int:
    # 1. Extract
    raw_text = extract_text_from_file(file_bytes, filename)
    if not raw_text:
        raw_text = "No text found in document."

    # 2 & 3. Structure and Evaluate (Combined into one powerful LLM call to save time/tokens)
    system_prompt = """You are an expert technical recruiter and ATS (Applicant Tracking System) analyzer.
Analyze the provided resume text. If a target job description is provided, evaluate the resume against it.
Return STRICTLY a JSON object matching this exact schema:
{
  "overall_score": int (0-100, representing the ATS compatibility score),
  "strengths": ["string"],
  "weaknesses": ["string" (List exact improvements needed to achieve a 100/100 ATS score AND missing/weak sections of the resume)],
  "existing_skills": ["string"],
  "missing_skills": ["string"],
  "suggested_courses": ["string"]
}
Be highly critical but constructive, focusing on ATS parseability, keyword match, and formatting.
"""

    user_prompt = f"RESUME TEXT:\n{raw_text}\n\n"
    if jd.strip():
        user_prompt += f"TARGET JOB DESCRIPTION:\n{jd.strip()}\n"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    raw_response = chat_completion(messages, response_format="json")

    # Parse
    try:
        data = json.loads(raw_response)
        overall_score = data.get("overall_score", 0)
        strengths = data.get("strengths", [])
        weaknesses = data.get("weaknesses", [])
        existing_skills = data.get("existing_skills", [])
        missing_skills = data.get("missing_skills", [])
        suggested_courses = data.get("suggested_courses", [])
    except json.JSONDecodeError:
        overall_score = 0
        strengths = ["Error analyzing resume"]
        weaknesses = []
        existing_skills = []
        missing_skills = []
        suggested_courses = []

    # 4. Persist
    analysis = ResumeAnalysis(
        user_id=user_id,
        filename=filename,
        target_job_description=jd,
        overall_score=overall_score,
        strengths=strengths,
        weaknesses=weaknesses,
        existing_skills=existing_skills,
        missing_skills=missing_skills,
        suggested_courses=suggested_courses,
        raw_ai_output=raw_response
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    return analysis.id
