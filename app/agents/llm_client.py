import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# We need a client singleton
_client = None

def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_groq_api_key_here":
            print("WARNING: GROQ_API_KEY not set. Using mock responses.")
            return None
        _client = Groq(api_key=api_key)
    return _client

def chat_completion(messages, response_format=None, model="llama-3.3-70b-versatile"):
    """
    Wrapper for Groq API.
    If response_format=="json", forces JSON mode.
    """
    client = get_client()
    
    # Mock fallback for local testing without API key
    if not client:
        if response_format == "json":
            return json.dumps({
                "ai_summary": "Mock summary based on traits.",
                "recommended_careers": [
                    {"name": "Data Scientist", "match": 92},
                    {"name": "AI/ML Engineer", "match": 88},
                    {"name": "Data Analyst", "match": 84},
                    {"name": "Software Developer", "match": 79},
                    {"name": "Business Intelligence", "match": 73}
                ]
            })
        return "Mock plain text response."

    kwargs = {
        "messages": messages,
        "model": model,
        "temperature": 0.7,
    }
    
    if response_format == "json":
        kwargs["response_format"] = {"type": "json_object"}

    try:
        response = client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        return content
    except Exception as e:
        print(f"Groq API Error: {e}")
        if response_format == "json":
            return "{}"
        return f"Error connecting to AI service."
