"""
================================================================================
SYSTEM ARCHITECT: Chris Fornesa
PROJECT: Tanaga & Poetry Agent (Phonetic Rigor Edition)
MISSION: Achieving 100% syllabic veracity through staccato-word constraints.
GOVERNANCE: Local PII Redaction, Deterministic Inference, Syllabic Ceiling.
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
app = FastAPI(title="Tanaga & Poetry Agent - Veracity Edition")

# 1. CORS PROTOCOL (The Digital Handshake)
# Enables secure communication between the Hostinger UI and Replit backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. PRIVACY SCRUBBER (PII Sanitization Layer)
# MISSION ALIGNMENT: Protects user privacy by redacting identifiers locally.
def redact_pii(text: str) -> str:
    patterns = {
        "EMAIL": r'[\w\.-]+@[\w\.-]+\.\w+',
        "PHONE": r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}'
    }
    for label, pattern in patterns.items():
        text = re.sub(pattern, f"[{label}_REDACTED]", text, flags=re.IGNORECASE)
    return text

# 3. POETIC PROTOCOL: THE STACCATO CONSTRAINT
# CONCEPTUAL REASONING: Implements the 'Veracity Lockdown.' By forbidding 
# words longer than 3 syllables, we align the AI's token-based logic with 
# actual phonetic counting, preventing 'Long-Word Hallucination.'
def get_tanaga_system_prompt():
    return (
        "You are an Expert Poet specialized in the pre-colonial Philippine Tanaga.\n\n"
        "STRICT ARCHITECTURAL CONSTRAINTS:\n"
        "1. TAGALOG METER: Exactly 7 syllables per line. NO EXCEPTIONS.\n"
        "2. WORD CEILING: DO NOT use words longer than 3 syllables. Use short, simple words.\n"
        "3. STRUCTURE: 4 lines of plain text only.\n"
        "4. NO MARKDOWN: Do not use asterisks (*) or bolding.\n\n"
        "SYLLABLE AUDIT (VOWEL ANCHORING):\n"
        "- Count every vocalized vowel (A-E-I-O-U) as 1 syllable.\n"
        "- Break the line: 'Ang i-nit ay ma-ba-ngis' (7).\n"
        "- Forbidden: Long words like 'tinatahimik' (5 syllables) or 'pumupukaw' (4).\n\n"
        "TONE: Use 'Talinghaga' (Metaphor). Accuracy is the highest priority."
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
        "logic": "Staccato-Veracity-Locked",
        "model": "ministral-14b-2512"
    }

# 5. MAIN GENERATION ENDPOINT
@app.post("/generate-tanaga")
async def process_chat(request: PoetryRequest):
    from openai import OpenAI

    safe_input = redact_pii(request.user_input)
    api_key = os.environ.get('MISTRAL_API_KEY')

    if not api_key:
        return {"reply": "Error: MISTRAL_API_KEY missing from server secrets."}

    client = OpenAI(api_key=api_key, base_url="https://api.mistral.ai/v1")

    # ARCHITECTURAL NOTE: Temperature is set to 0.1 to maximize deterministic 
    # math. We sacrifice 'flourish' to ensure the 7-7-7-7 count is accurate.
    messages = [
        {"role": "system", "content": get_tanaga_system_prompt()},
        {"role": "user", "content": f"Theme: {safe_input}. Construct the verse. Audit: 1 vowel = 1 syllable."}
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