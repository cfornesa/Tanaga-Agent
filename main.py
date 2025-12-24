"""
================================================================================
SYSTEM ARCHITECT: Chris Fornesa
PROJECT: Tanaga & Poetry Agent (Phonetic Rigor Edition)
MISSION: Achieving 100% syllabic veracity via staccato-word constraints.
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
# CONCEPTUAL REASONING: Minimizing overhead ensures that the "Thinking Time" 
# is dedicated to phonetic auditing rather than server latency.
app = FastAPI(title="Tanaga & Poetry Agent - Veracity Edition")

# 1. CORS PROTOCOL (The Digital Handshake)
# CONCEPTUAL REASONING: This enables secure Cross-Origin communication between 
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

# 3. POETIC PROTOCOL: THE STACCATO CONSTRAINT
# CONCEPTUAL REASONING: This framework addresses the "Phonetic Math" limitation 
# of LLMs. By using "Staccato Instructions," we force the model to prioritize 
# structural rigidness (Syllabic Anchoring) over creative linguistic drift.
def get_tanaga_system_prompt():
    return (
        "You are an Expert Poet specialized in the pre-colonial Philippine Tanaga.\n\n"
        "STRICT ARCHITECTURAL CONSTRAINTS:\n"
        "1. TAGALOG METER: Exactly 7 syllables per line. NO EXCEPTIONS.\n"
        "2. ENGLISH METER: Exactly 8 syllables per line. NO EXCEPTIONS.\n"
        "3. WORD CEILING: DO NOT use words longer than 3 syllables. Use short, simple words.\n"
        "4. STRUCTURE: Exactly 4 lines of plain text only.\n"
        "5. NO MARKDOWN: Do not use asterisks (*) or bolding.\n\n"
        "SYLLABLE CALCULATION (INTERNAL ONLY):\n"
        "- Count every vocalized vowel (A-E-I-O-U) as 1 syllable.\n"
        "- Break the line: 'Ang i-nit ay ma-ba-ngis' (7).\n"
        "- Forbidden: Long words like 'tinatawag' or 'pumupukaw'.\n\n"
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

    # DYNAMIC LANGUAGE DETECTION
    # CONCEPTUAL REASONING: Detects user intent for Tagalog or English to 
    # dynamically shift the prosodic meter between 7 and 8 syllables.
    user_query_lower = safe_input.lower()
    tagalog_triggers = ["tagalog", "sa tagalog", "filipino", "tag-alog"]
    is_tagalog = any(trigger in user_query_lower for trigger in tagalog_triggers)

    if is_tagalog:
        target_lang = "Tagalog (7 syllables per line)"
    else:
        target_lang = "English (8 syllables per line)"

    messages = [
        {"role": "system", "content": get_tanaga_system_prompt()},
        {"role": "user", "content": f"Write a Tanaga in {target_lang} about: {safe_input}."}
    ]

    try:
        # Utilizing Ministral 14B for vowel-count auditing.
        response = client.chat.completions.create(
            model="ministral-14b-latest", 
            messages=messages,
            # CONCEPTUAL REASONING: Temperature 0.1 maximizes deterministic math. 
            # We sacrifice 'creative flourish' for structural veracity.
            temperature=0.1, 
            max_tokens=200
        )

        reply_text = response.choices[0].message.content

        # STEP 6: RESOURCE CONSERVATION (Garbage Collection)
        # CONCEPTUAL REASONING: Explicit memory management is used to prevent 
        # "RAM Creep" in the Replit environment, following Green AI principles.
        del messages, safe_input
        gc.collect()

        return {"reply": reply_text.strip()}

    except Exception as e:
        gc.collect()
        return {"reply": f"System Error: {str(e)}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")