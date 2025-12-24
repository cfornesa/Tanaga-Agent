"""
================================================================================
SYSTEM ARCHITECT: Chris Fornesa
PROJECT: Tanaga & Poetry Agent (Vowel-Veracity Edition)
MISSION: Achieving absolute 7-7-7-7 metrics through monosyllabic anchoring.
GOVERNANCE: Local PII Redaction, Deterministic Inference (Temp 0.1).
================================================================================
"""

import os
import re
import gc
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

# INITIALIZATION: FastAPI selected for high-concurrency async performance.
# CONCEPTUAL REASONING: Minimizing overhead ensures that the "Thinking Time" 
# is dedicated to phonetic auditing rather than server latency.
app = FastAPI(title="Tanaga & Poetry Agent - Vowel-Veracity Edition")

# 1. CORS PROTOCOL (The Digital Handshake)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. PRIVACY SCRUBBER (PII Sanitization Layer)
# CONCEPTUAL REASONING: Implements "Privacy-by-Design." By scrubbing identifiers 
# locally, we ensure data sovereignty before the verse is generated.
def redact_pii(text: str) -> str:
    patterns = {
        "EMAIL": r'[\w\.-]+@[\w\.-]+\.\w+',
        "PHONE": r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}'
    }
    for label, pattern in patterns.items():
        text = re.sub(pattern, f"[{label}_REDACTED]", text, flags=re.IGNORECASE)
    return text

# 3. POETIC PROTOCOL: MONOSYLLABIC ANCHORING
# CONCEPTUAL REASONING: This protocol addresses "Tokenization Hallucination." 
# By mandating a vowel-by-vowel audit and forbidding complex words like 
# "tinatahimik," we align the AI's math with Tagalog phonetics.
def get_tanaga_system_prompt():
    return (
        "You are an Expert Poet specialized in the pre-colonial Tagalog Tanaga.\n\n"
        "STRICT ARCHITECTURAL CONSTRAINTS:\n"
        "1. TAGALOG METER: Exactly 7 syllables per line. NO EXCEPTIONS.\n"
        "2. VOWEL AUDIT: Every vowel (A, E, I, O, U) counts as exactly 1 syllable.\n"
        "3. WORD LIMIT: Do not use words with more than 3 syllables.\n"
        "4. NO MARKDOWN: Plain text only. 4 lines total.\n\n"
        "EXAMPLE AUDIT:\n"
        "- 'Ang i-nit ay ma-ba-ngis' (7 vowels = 7 syllables).\n"
        "- 'Ang tu-big ay ma-lam-ig' (7 vowels = 7 syllables).\n\n"
        "TONE: Use deep metaphor (Talinghaga). Math is the priority."
    )

class PoetryRequest(BaseModel):
    user_input: str
    history: List[Dict] = []

# 4. HEALTH CHECK (System Vitality)
@app.get("/")
async def health_check():
    return {
        "status": "online", 
        "agent": "Tanaga Poet",
        "logic": "Monosyllabic-Anchoring-Enabled",
        "model": "ministral-14b-2512"
    }

# 5. MAIN GENERATION ENDPOINT
@app.post("/generate-tanaga")
async def process_chat(request: PoetryRequest):
    from openai import OpenAI

    safe_input = redact_pii(request.user_input)
    api_key = os.environ.get('MISTRAL_API_KEY')

    if not api_key:
        return {"reply": "Error: MISTRAL_API_KEY not configured."}

    client = OpenAI(api_key=api_key, base_url="https://api.mistral.ai/v1")

    # ARCHITECTURAL NOTE: Temperature is set to 0.1. This forces the model 
    # to be deterministic, favoring correct syllable math over creative "drift."
    messages = [
        {"role": "system", "content": get_tanaga_system_prompt()},
        {"role": "user", "content": f"Theme: {safe_input}. Write a 7-7-7-7 Tagalog Tanaga. Count the vowels to be sure."}
    ]

    try:
        response = client.chat.completions.create(
            model="ministral-14b-latest", 
            messages=messages,
            temperature=0.1, 
            max_tokens=200
        )

        reply_text = response.choices[0].message.content

        # STEP 6: RESOURCE CONSERVATION (Garbage Collection)
        del messages, safe_input
        gc.collect()

        return {"reply": reply_text.strip()}

    except Exception as e:
        gc.collect()
        return {"reply": f"System Error: {str(e)}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")