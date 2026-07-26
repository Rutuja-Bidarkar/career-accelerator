import json
import uuid
from typing import Dict, Any
from app.agents.llm_client import chat_completion

# In-memory session store (dictionary). 
# For production, this could be Redis.
ACTIVE_SESSIONS: Dict[str, Dict[str, Any]] = {}

def create_interview_session(job_role: str) -> str:
    session_id = str(uuid.uuid4())
    
    # 1. Plan: Generate a structured question plan
    system_prompt = f"""You are an expert technical interviewer planning a 5-question interview for a {job_role}.
Generate a plan with exactly 5 questions (1 intro, 2 technical, 1 behavioral, 1 scenario).
Return strictly JSON:
{{
  "questions": ["Q1", "Q2", "Q3", "Q4", "Q5"]
}}"""
    
    raw_plan = chat_completion([{"role": "system", "content": system_prompt}], response_format="json")
    
    try:
        plan = json.loads(raw_plan).get("questions", [])
        if not plan or len(plan) < 5:
            raise ValueError("Invalid plan")
    except Exception:
        # Fallback plan
        plan = [
            f"Tell me about yourself and your interest in the {job_role} role.",
            f"What is your strongest technical skill related to being a {job_role}?",
            f"Describe a complex problem you solved recently.",
            f"How do you handle disagreements with a team member?",
            f"Where do you see your career heading in the next 3 years?"
        ]

    ACTIVE_SESSIONS[session_id] = {
        "job_role": job_role,
        "question_plan": plan,
        "current_index": 0,
        "transcript": [],
        "follow_up_depth": 0,  # tracks if we are currently asking a follow-up
        "is_finished": False
    }
    
    return session_id

def get_next_question(session_id: str) -> str:
    session = ACTIVE_SESSIONS.get(session_id)
    if not session or session["is_finished"]:
        return "Interview is complete."
        
    idx = session["current_index"]
    if idx < len(session["question_plan"]):
        q = session["question_plan"][idx]
        session["transcript"].append({"role": "interviewer", "message": q})
        return q
    else:
        session["is_finished"] = True
        return "Thank you, that concludes our interview."

def process_answer(session_id: str, answer: str) -> str:
    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        return "Session expired."
        
    session["transcript"].append({"role": "candidate", "message": answer})
    
    # Evaluate + Branch
    # Should we ask a follow-up? Max 1 follow-up per planned question.
    if session["follow_up_depth"] == 0:
        last_q = session["question_plan"][session["current_index"]]
        eval_prompt = f"""You are the interviewer. 
Job Role: {session["job_role"]}
Question asked: "{last_q}"
Candidate answered: "{answer}"

Evaluate the answer. Does it lack detail or require a targeted follow-up question to probe deeper? 
If YES, generate a short follow-up question.
If NO, output exactly "PROCEED".
"""
        response = chat_completion([{"role": "user", "content": eval_prompt}])
        
        if "PROCEED" not in response.upper() and "?" in response:
            session["follow_up_depth"] += 1
            session["transcript"].append({"role": "interviewer", "message": response.strip()})
            return response.strip()

    # Move to next planned question
    session["current_index"] += 1
    session["follow_up_depth"] = 0
    return get_next_question(session_id)

def end_interview_session(session_id: str) -> dict:
    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        return {"score": 0, "summary": "Session not found."}
        
    # Generate summary
    transcript_text = "\n".join([f"{msg['role'].upper()}: {msg['message']}" for msg in session["transcript"]])
    
    eval_prompt = f"""You are an expert interviewer evaluating a candidate for a {session["job_role"]} role based on this transcript:
{transcript_text}

Provide a structured evaluation in JSON:
{{
  "score": int (0-100),
  "summary": "Detailed paragraph evaluating performance, strengths, and areas to improve."
}}
"""
    raw_eval = chat_completion([{"role": "user", "content": eval_prompt}], response_format="json")
    
    try:
        eval_data = json.loads(raw_eval)
        score = eval_data.get("score", 70)
        summary = eval_data.get("summary", "Good effort.")
    except Exception:
        score = 70
        summary = "Could not generate detailed summary."
        
    session["performance_summary"] = summary
    session["score"] = score
    session["is_finished"] = True
    
    return {
        "score": score,
        "summary": summary,
        "transcript": session["transcript"],
        "job_role": session["job_role"]
    }

def pop_session(session_id: str):
    """Remove and return session data for DB persistence."""
    return ACTIVE_SESSIONS.pop(session_id, None)
