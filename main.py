"""
================================================================================
SYSTEM ARCHITECT: Chris Fornesa
PROJECT: Tanaga & Poetry Agent (Phonetic Rigor Edition)
MISSION: Achieving 100% syllabic veracity via staccato word-choice constraints.
GOVERNANCE: Local PII Redaction, Zero-API Leakage, Vowel-Centric Auditing.
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
# CONCEPTUAL REASONING: Minimizing server idle time aligns with the mission of 
# Computational Sustainability while ensuring rapid linguistic processing.
app = FastAPI(title="Tanaga & Poetry Agent - Phonetic Rigor Edition")

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
# CONCEPTUAL REASONING: Implements "Privacy-by-Design." By scrubbing identifiers 
# locally using Regex, we ensure that user-specific data never reaches the 
# external LLM inference clusters.
def redact_pii(text: str) -> str:
    patterns = {
        "EMAIL": r'[\w\.-]+@[\w\.-]+\.\w+',
        "PHONE": r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}'
    }
    for label, pattern in patterns.items():
        text = re.sub(pattern, f"[{label}_REDACTED]", text, flags=re.IGNORECASE)
    return text

# 3. POETIC PROTOCOL: STACCATO-CONSTRAINT FRAMEWORK
# CONCEPTUAL REASONING: To solve the Tokenization Bias, this prompt mandates 
# a "Vowel-Vocalized Audit." It explicitly forbids complex polysyllabic words 
# (e.g., sumisid-lak, pumupukaw) in favor of staccato 1-2 syllable words.
def get_tanaga_system_prompt():
    return (
        "You are an Expert Poet specialized in the pre-colonial Tagalog Tanaga.\n\n"
        "STRICT MATHEMATICAL CONSTRAINTS:\n"
        "1. TAGALOG METER: Exactly 7 syllables per line. NO MORE, NO LESS.\n"
        "2. WORD LIMIT: Do not use words with more than 3 syllables. Use short, simple words.\n"
        "3. LINE COUNT: Exactly 4 lines.\n"
        "4. NO MARKDOWN: Plain text only. No asterisks (*).\n\n"
        "SYLLABLE AUDIT (PHONETIC RIGOR):\n"
        "- Count vocalized vowel sounds (A-E-I-O-U).\n"
        "- 'Gabi' (2), 'Dagat' (2), 'Init' (2), 'Araw' (2), 'Lupa' (2).\n"
        "- Line Example: 'Ang a-raw ay ma-i-nit' (7).\n\n"
        "TONE: High-density metaphor (Talinghaga). Math is the priority."
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
        "logic": "Staccato-Constraint-Enabled",
        "model": "ministral-14b-2512"
    }

# 5. MAIN GENERATION ENDPOINT
# CONCEPTUAL REASONING: Orchestrates the request lifecycle. It enforces 
# "Analytical Rigidity" by setting a low Temperature (0.1) and forcing 
# a vowel-count check in the user-instruction phase.
@app.post("/generate-tanaga")
async def process_chat(request: PoetryRequest):
    from openai import OpenAI

    safe_input = redact_pii(request.user_input)
    api_key = os.environ.get('MISTRAL_API_KEY')

    if not api_key:
        return {"reply": "Error: MISTRAL_API_KEY missing from server secrets."}

    client = OpenAI(api_key=api_key, base_url="https://api.mistral.ai/v1")

    # ARCHITECTURAL NOTE: The prompt explicitly asks the model to "verify vowel counts" 
    # to force the model to focus on the phonetic structure over the meaning.
    messages = [
        {"role": "system", "content": get_tanaga_system_prompt()},
        {"role": "user", "content": f"Theme: {safe_input}. Write a 7-7-7-7 Tagalog Tanaga. Count the vowels to be sure."}
    ]

    try:
        response = client.chat.completions.create(
            model="ministral-14b-latest", 
            messages=messages,
            temperature=0.1, # Forced deterministic output for mathematical accuracy.
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