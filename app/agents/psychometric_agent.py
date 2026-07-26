import json
from sqlalchemy.orm import Session
from app.models import CareerCategory, PsychometricQuestion, PsychometricResult
from app.agents.llm_client import chat_completion

def run_psychometric_pipeline(db: Session, user_id: int, answers_dict: dict) -> int:
    """
    Two-stage pipeline:
    1. Deterministic scorer based on trait_tags.
    2. LLM interpreter to generate summary and pick categories.
    Returns the new PsychometricResult ID.
    """
    # 1. Deterministic Scorer
    # Fetch all questions to get their tags
    questions = db.query(PsychometricQuestion).all()
    q_map = {str(q.id): q.trait_tag for q in questions}
    
    trait_scores = {}
    for q_id_str, val in answers_dict.items():
        tag = q_map.get(q_id_str)
        if tag:
            try:
                score = int(val)
                trait_scores[tag] = trait_scores.get(tag, 0) + score
            except (ValueError, TypeError):
                pass

    # 2. LLM Interpreter
    categories = db.query(CareerCategory).all()
    cat_list = [f"{c.slug} ({c.name})" for c in categories]
    
    system_prompt = f"""You are an expert career counselor AI.
Analyze the user's trait scores across all dimensions: interests, personality, aptitude, skills, and values.
Provide a concise 3-5 sentence natural language Candidate Profile summarizing their strengths and work style.
Then, recommend the top 5 specific career paths for them based heavily on their specific traits along with a match percentage (e.g. 92, 88).

IMPORTANT: Provide diverse and accurate career paths based on the user's actual traits. DO NOT just copy the example JSON structure below. The data in the JSON below is strictly an EXAMPLE of the schema format!

Return strictly in this JSON format:
{{
  "ai_summary": "Your concise 3-5 sentence candidate profile here.",
  "recommended_careers": [
    {{"name": "Data Scientist", "match": 92}},
    {{"name": "AI/ML Engineer", "match": 88}},
    {{"name": "Data Analyst", "match": 84}},
    {{"name": "Software Developer", "match": 79}},
    {{"name": "Business Intelligence", "match": 73}}
  ]
}}
"""
    
    user_prompt = f"Trait Scores: {json.dumps(trait_scores)}"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    raw_response = chat_completion(messages, response_format="json")
    
    try:
        result_data = json.loads(raw_response)
        summary = result_data.get("ai_summary", "Unable to generate summary.")
        rec_careers = result_data.get("recommended_careers", [])
    except json.JSONDecodeError:
        summary = "Error parsing AI response."
        rec_careers = []

    # Persist
    result = PsychometricResult(
        user_id=user_id,
        answers=answers_dict,
        trait_scores=trait_scores,
        recommended_careers=rec_careers,
        ai_summary=summary
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    
    return result.id
