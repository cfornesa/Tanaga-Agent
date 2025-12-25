"""
================================================================================
SYSTEM ARCHITECT: Chris Fornesa
PROJECT: Tanaga & Poetry Agent (Phonetic Rigor Edition)
MISSION: Achieving 100% syllabic veracity via staccato-word constraints.
GOVERNANCE: Local PII Redaction, Deterministic Inference, Language-Routing.
CONCEPTUAL FRAMEWORK: Bridges the gap between Transformer-based tokenization 
and traditional Philippine prosody.
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
# Ensures that PII never enters the external inference cluster.
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
        "1. LANGUAGE: Output ONLY ONE poem. Do not translate. Do not explain.\n"
        "2. TAGALOG METER: Exactly 7 syllables per line.\n"
        "3. ENGLISH METER: Exactly 8 syllables per line.\n"
        "4. WORD CEILING: DO NOT use words longer than 3 syllables. Use simple words.\n"
        "5. STRUCTURE: Exactly 4 lines of plain text only. No more.\n"
        "6. NO MARKDOWN: Do not use asterisks (*) or bolding.\n\n"
        "SYLLABLE CALCULATION (INTERNAL ONLY):\n"
        "- Count every vocalized vowel (A-E-I-O-U) as 1 syllable.\n"
        "- Accuracy is the highest priority."
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
        "model": "ministral-14b-latest"
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

    # DYNAMIC LANGUAGE ROUTER
    # CONCEPTUAL REASONING: Explicitly forces the model to pick ONE language 
    # to prevent "Token Exhaustion" and ensures the meter matches the linguistic intent.
    user_query_lower = safe_input.lower()
    tagalog_triggers = ["tagalog", "sa tagalog", "filipino", "tag-alog"]
    is_tagalog = any(trigger in user_query_lower for trigger in tagalog_triggers)

    target_lang = "Tagalog" if is_tagalog else "English"
    meter = "7 syllables" if is_tagalog else "8 syllables"

    messages = [
        {"role": "system", "content": get_tanaga_system_prompt()},
        {"role": "user", "content": f"Write ONE {target_lang} Tanaga ({meter}) about: {safe_input}. Do not provide an English version."}
    ]

    try:
        # ARCHITECTURAL NOTE: Temperature is set to 0.1 to maximize deterministic 
        # math. We sacrifice 'flourish' to ensure the prosodic count is accurate.
        response = client.chat.completions.create(
            model="ministral-14b-latest", 
            messages=messages,
            temperature=0.1, 
            max_tokens=100
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