import os
import re
import gc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Tanaga Auditor Agent")

# 1. CORS CONFIGURATION: Bridges Hostinger frontend and Replit backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. PRECISION PRIVACY SCRUBBER: Targets only specific contact strings.
def redact_pii(text: str) -> str:
    patterns = {
        "EMAIL": r'[\w\.-]+@[\w\.-]+\.\w+',
        "PHONE": r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}'
    }
    for label, pattern in patterns.items():
        text = re.sub(pattern, f"[{label}_REDACTED]", text, flags=re.IGNORECASE)
    return text

# 3. CONSTRAINED GAIL FRAMEWORK (Short-Word Lockdown)
def get_tanaga_system_prompt():
    """
    GOALS: Stop count hallucinations by limiting word length.
    ACTIONS: 
        - STRICT METER: Every line must have exactly 7 vowel sounds (A-E-I-O-U).
        - FORBIDDEN: Do not use words with 3+ syllables (e.g., 'dumating', 'tahimik').
        - VOCAL TRUTH: 'Mga' counts as 2 vowels (Ma-nga).
    """
    return (
        "You are a strict Syllabic Engine for the Filipino Tanaga. "
        "Your only goal is a 4-line poem where each line has exactly 7 vowel sounds.\n\n"
        "STRICT CONSTRAINTS:\n"
        "1. NO LONG WORDS: You are forbidden from using 3-syllable or 4-syllable words. Use only 1-2 syllable words.\n"
        "2. VOWEL COUNTING: Count the vocalized sounds (A, E, I, O, U). \n"
        "   - 'Sa la-ngit' = 3 vowel sounds.\n"
        "   - 'Ma-nga' = 2 vowel sounds.\n"
        "3. FORMAT: Output only the 4 lines. No explanations or audits.\n\n"
        "TONE: Deterministic and precise."
    )

class PoetryRequest(BaseModel):
    user_input: str
    history: List[Dict] = []

# 4. HEALTH CHECK
@app.get("/")
async def health():
    return {"status": "Syllabic Engine Online", "constraints": "Locked"}

# 5. MAIN GENERATION ENDPOINT
@app.post("/generate-tanaga")
async def process_chat(request: PoetryRequest):
    from openai import OpenAI

    # Redact input locally
    safe_input = redact_pii(request.user_input)

    client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

    # Construct message
    messages = [
        {"role": "system", "content": get_tanaga_system_prompt()},
        {"role": "user", "content": f"Theme: {safe_input}"}
    ]

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            # TEMPERATURE 0.0: Removes all creative variance to enforce strict syllable math.
            temperature=0.0
        )

        reply = response.choices[0].message.content

        # 6. MEMORY MANAGEMENT
        del messages, safe_input
        gc.collect()

        return {"reply": reply}
    except Exception as e:
        gc.collect()
        return {"error": f"Logic error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)