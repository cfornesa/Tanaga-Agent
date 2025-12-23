import os
import re
import gc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Tanaga Poetry Agent")

# 1. CORS CONFIGURATION: Essential for Replit-to-Hostinger handshake.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. OPTIMIZED PRIVACY SCRUBBER: Thinned to prevent over-redaction of Tagalog text.
def redact_pii(text: str) -> str:
    # Only scrubs actual high-risk contact strings; avoids broad regex that eats art.
    patterns = {
        "EMAIL": r'[\w\.-]+@[\w\.-]+\.\w+',
        "PHONE": r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}'
    }
    for label, pattern in patterns.items():
        text = re.sub(pattern, f"[{label}_REDACTED]", text, flags=re.IGNORECASE)
    return text

# 3. INTEGRATED GAIL FRAMEWORK (Vowel-Centric Phonetic Protocol)
def get_tanaga_system_prompt():
    """
    GOALS: Generate 7-7-7-7 Tanagas by counting vowel sounds (A-E-I-O-U).
    ACTIONS: 
        - VOWEL COUNTING: Every vocalized vowel is 1 syllable. 
        - VOCAL TRUTH: 'Mga' is 2 (Ma-nga). 'Sa ilalim' is 4 (Sa-i-la-lim).
        - REJECTION: If a line exceeds 7 vowel sounds, you MUST rewrite it.
    """
    return (
        "You are a Master of the Traditional Filipino Tanaga. You use Vowel-Sound Logic.\n\n"
        "STRICT COMPOSITION RULES:\n"
        "1. VOCAL COUNT: Count the vowel sounds (A, E, I, O, U) in every word.\n"
        "2. THE MGA RULE: 'Mga' is Ma-nga (2 vowels). 'Puno't' is Pu-not (2 vowels).\n"
        "3. NO CHEATING: Do not label a line as 7 if it has 8 or more vowel sounds.\n\n"
        "STRUCTURE:\n"
        "Line 1: 7 Vowel Sounds\n"
        "Line 2: 7 Vowel Sounds\n"
        "Line 3: 7 Vowel Sounds\n"
        "Line 4: 7 Vowel Sounds\n\n"
        "TONE: Poetic but mathematically precise. Provide the Poem first, then a Vowel-Breakdown."
    )

class PoetryRequest(BaseModel):
    user_input: str
    history: List[Dict] = []

# 4. HEALTH CHECK
@app.get("/")
async def health():
    return {"status": "Vowel-Logic Auditor Active", "privacy": "Thinned-Mode"}

# 5. MAIN CHAT ENDPOINT
@app.post("/generate-tanaga")
async def process_chat(request: PoetryRequest):
    from openai import OpenAI

    # Redact input locally (Safe Scrub)
    safe_input = redact_pii(request.user_input)

    client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

    messages = [{"role": "system", "content": get_resume_system_prompt() if "resume" in safe_input.lower() else get_tanaga_system_prompt()}]
    messages.append({"role": "user", "content": safe_input})

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            # Temperature 0.1 prevents the AI from choosing 'pretty' words that break the meter.
            temperature=0.1
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