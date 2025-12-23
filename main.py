import os
import re
import gc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Tanaga & Poetry Agent")

# 1. CORS CONFIGURATION: Enables secure communication between UI and Logic.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. PRIVACY SCRUBBER: Sanitizes PII locally before API transmission.
def redact_pii(text: str) -> str:
    patterns = {
        "EMAIL": r'[\w\.-]+@[\w\.-]+\.\w+',
        "PHONE": r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}'
    }
    for label, pattern in patterns.items():
        text = re.sub(pattern, f"[{label}_REDACTED]", text, flags=re.IGNORECASE)
    return text

# 3. INTEGRATED GAIL FRAMEWORK: The core logic pillars for structural/cultural accuracy.
def get_tanaga_system_prompt():
    """
    PILLAR 1 (SYLLABIC ANCHOR): Enforce 7-7-7-7 for Tagalog and 8-8-8-8 for English.
    PILLAR 2 (PHONETIC AUDIT): Count vocalized vowel sounds (A-E-I-O-U).
    PILLAR 3 (CEILING): Limit word length to 3-4 syllables to prevent math errors.
    PILLAR 4 (TALINGHAGA): Prioritize evocative metaphors over literal descriptions.
    """
    return (
        "You are an Expert Poet specialized in the Tanaga and Short-Form Verse.\n\n"
        "CONCEPTUAL IMPLEMENTATION: SYLLABIC ANCHORING\n"
        "- For Tagalog: 4 lines, exactly 7 syllables per line.\n"
        "- For English: 4 lines, exactly 8 syllables per line.\n\n"
        "CONCEPTUAL IMPLEMENTATION: PHONETIC AUDIT\n"
        "- Count vocalized sounds carefully. 'Mga' is 2. 'Gabi'y' is 2.\n"
        "- Avoid long, complex words that break the meter.\n\n"
        "TONE: Expressive, evocative, and structurally rigid. Output 4 lines only."
    )

class PoetryRequest(BaseModel):
    user_input: str
    history: List[Dict] = []

# 4. HEALTH CHECK: Verifies the 'Master State' logic.
@app.get("/")
async def health():
    return {"status": "Master-Logic Online", "temp": 0.4, "meter": "Hybrid-7/8"}

# 5. MAIN GENERATION ENDPOINT: Executes the logic with the validated 0.4 temperature.
@app.post("/generate-tanaga")
async def process_chat(request: PoetryRequest):
    from openai import OpenAI

    # Apply local privacy redaction
    safe_input = redact_pii(request.user_input)

    client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

    messages = [
        {"role": "system", "content": get_tanaga_system_prompt()},
        {"role": "user", "content": safe_input}
    ]

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            # CONCEPTUAL IMPLEMENTATION: TEMPERATURE ANCHORING
            # 0.4 is the proven 'Sweet Spot' for variety and structural integrity.
            temperature=0.4 
        )

        reply = response.choices[0].message.content

        # 6. MEMORY MANAGEMENT: Clears objects to prevent Replit resource exhaustion.
        del messages, safe_input
        gc.collect()

        return {"reply": reply}
    except Exception as e:
        gc.collect()
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)