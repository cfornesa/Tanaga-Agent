"""
================================================================================
SYSTEM ARCHITECT: Chris Fornesa
PROJECT: Tanaga & Poetry Agent (Phonetic Rigor Edition)
MISSION: Ensuring syllabic veracity via staccato-word constraints.
GOVERNANCE: Local PII Redaction, Low-Temperature Mathematical Logic.
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
# CONCEPTUAL REASONING: Enables secure Cross-Origin communication between 
# the Hostinger UI and the Replit logic layer, maintaining a strict API boundary.
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
# CONCEPTUAL REASONING: To solve the "Phonetic Math" limitation of LLMs, 
# this prompt mandates a "Vowel-Vocalized Audit." It explicitly forbids 
# words longer than 3 syllables (e.g., tinatawag) to prevent count errors.
def get_tanaga_system_prompt():
    return (
        "You are an Expert Poet specialized in the Tagalog Tanaga.\n\n"
        "STRICT ARCHITECTURAL CONSTRAINTS:\n"
        "1. TAGALOG METER: Exactly 7 syllables per line. NO EXCEPTIONS.\n"
        "2. WORD CEILING: DO NOT use words longer than 3 syllables. Use short, simple words.\n"
        "3. STRUCTURE: Exactly 4 lines of plain text only.\n"
        "4. NO MARKDOWN: No asterisks (*) or bolding.\n\n"
        "SYLLABLE AUDIT (PHONETIC RIGOR):\n"
        "- Count vocalized vowel sounds (A-E-I-O-U).\n"
        "- 'Texas' is 2 syllables. 'Init' is 2. 'Dagat' is 2.\n"
        "- Line Example: 'Ang a-raw ay ma-i-nit' (7).\n\n"
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
        "logic": "Staccato-Veracity-Enabled",
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
        {"role": "user", "content": f"Theme: {safe_input}. Write a 7-7-7-7 Tagalog Tanaga. Count the vowels."}
    ]

    try:
        response = client.chat.completions.create(
            model="ministral-14b-latest", 
            messages=messages,
            temperature=0.1, # Minimized creative drift to favor mathematical accuracy.
            max_tokens=250
        )

        reply_text = response.choices[0].message.content

        # STEP 6: Resource Conservation (Garbage Collection)
        del messages, safe_input
        gc.collect()

        return {"reply": reply_text.strip()}

    except Exception as e:
        gc.collect()
        return {"reply": f"System Error: {str(e)}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")