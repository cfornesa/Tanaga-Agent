import os
import re
import gc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Tanaga Syllabic Engine")

# 1. CORS CONFIGURATION: Enables Hostinger-to-Replit secure requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. PRIVACY SCRUBBER: Targets specific high-risk PII patterns.
def redact_pii(text: str) -> str:
    patterns = {
        "EMAIL": r'[\w\.-]+@[\w\.-]+\.\w+',
        "PHONE": r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}'
    }
    for label, pattern in patterns.items():
        text = re.sub(pattern, f"[{label}_REDACTED]", text, flags=re.IGNORECASE)
    return text

# 3. CONSTRAINED GAIL FRAMEWORK (Last Mile Precision)
def get_tanaga_system_prompt():
    """
    GOALS: Achieve structural perfection (7-7-7-7) via vocabulary restriction.
    ACTIONS: 
        - 3-SYLLABLE CEILING: FORBIDDEN to use any word with 4+ syllables.
        - ROOT WORD STRATEGY: Use simple root words instead of long conjugated verbs.
        - VOWEL COUNTING: Every vowel sound (A, E, I, O, U) is 1 unit. 
    """
    return (
        "You are a strict Syllabic Engine for the Filipino Tanaga. "
        "Each line MUST have exactly 7 vowel sounds.\n\n"
        "STRICT CONSTRAINTS:\n"
        "1. WORD LIMIT: Do not use words with 4 or more syllables. (e.g., 'nananahimik' is FORBIDDEN).\n"
        "2. VOWEL RULE: Count vowels. 'Umiihip' is 4 vowels. 'Umihip' is 3.\n"
        "3. LAST MILE FIX: If a line is too long, replace long verbs with short adjectives.\n"
        "4. FORMAT: Output only the 4-line poem. No other text.\n\n"
        "TONE: Deterministic."
    )

class PoetryRequest(BaseModel):
    user_input: str
    history: List[Dict] = []

# 4. HEALTH CHECK
@app.get("/")
async def health():
    return {"status": "Last-Mile Engine Active", "rules": "3-Syllable-Ceiling"}

# 5. GENERATION ENDPOINT
@app.post("/generate-tanaga")
async def process_chat(request: PoetryRequest):
    from openai import OpenAI

    # Redact input locally
    safe_input = redact_pii(request.user_input)

    client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

    # Construct strictly constrained message
    messages = [
        {"role": "system", "content": get_tanaga_system_prompt()},
        {"role": "user", "content": f"Theme: {safe_input}"}
    ]

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            # DETERMINISTIC SETTING: Stops creative wandering.
            temperature=0.0
        )

        reply = response.choices[0].message.content

        # 6. MEMORY MANAGEMENT
        del messages, safe_input
        gc.collect()

        return {"reply": reply}
    except Exception as e:
        gc.collect()
        return {"error": f"Process Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)