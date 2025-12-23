import os
import re
import gc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Tanaga Syllabic Engine")

# 1. CORS CONFIGURATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. PRIVACY SCRUBBER (Essential for PII protection)
def redact_pii(text: str) -> str:
    patterns = {
        "EMAIL": r'[\w\.-]+@[\w\.-]+\.\w+',
        "PHONE": r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}'
    }
    for label, pattern in patterns.items():
        text = re.sub(pattern, f"[{label}_REDACTED]", text, flags=re.IGNORECASE)
    return text

# 3. CONSTRAINED GAIL FRAMEWORK (The "Vowel Anchor" Protocol)
def get_tanaga_system_prompt():
    """
    GOALS: 7-7-7-7 structure with evocative metaphors (Talinghaga).
    ACTIONS: 
        - VOWEL ANCHOR: You must count exactly 7 vowel sounds per line.
        - WORD LIMIT: Forbidden to use words with 4+ syllables.
        - ERROR CORRECTION: 'Yelo' is 2 syllables. 'Balat' is 2 syllables. 
    """
    return (
        "You are a Master of the Traditional Filipino Tanaga. "
        "Your goal is a 4-line poem with exactly 7 syllables per line.\n\n"
        "STRICT PHONETIC RULES:\n"
        "1. VOWEL COUNT: Every line MUST have exactly 7 vowel sounds (A, E, I, O, U).\n"
        "2. NO 8-SYLLABLE DRIFT: Be careful with words like 'balat' (2) or 'yelo' (2). \n"
        "   - 'Kagat ng yelo sa balat' is 8 syllables. This is a FAILURE.\n"
        "   - 'Kagat ng yelo sa loob' is 7 syllables. This is a SUCCESS.\n"
        "3. TALINGHAGA: Use evocative, creative metaphors, not literal descriptions.\n\n"
        "OUTPUT: 4 lines only. No analysis."
    )

class PoetryRequest(BaseModel):
    user_input: str
    history: List[Dict] = []

# 4. HEALTH CHECK
@app.get("/")
async def health():
    return {"status": "Anchor-Engine Online", "temp": "0.4"}

# 5. GENERATION ENDPOINT
@app.post("/generate-tanaga")
async def process_chat(request: PoetryRequest):
    from openai import OpenAI

    safe_input = redact_pii(request.user_input)
    client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

    messages = [
        {"role": "system", "content": get_tanaga_system_prompt()},
        {"role": "user", "content": f"Theme: {safe_input}"}
    ]

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            # TEMPERATURE 0.4: The 'Creative Sweet Spot'—provides variety without total math collapse.
            temperature=0.4
        )

        reply = response.choices[0].message.content
        del messages, safe_input
        gc.collect()
        return {"reply": reply}
    except Exception as e:
        gc.collect()
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)