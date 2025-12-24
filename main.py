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

app = FastAPI(title="Tanaga & Poetry Agent - Veracity Edition")

# 1. CORS PROTOCOL (The Digital Handshake)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. PRIVACY SCRUBBER (PII Sanitization Layer)
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
        "SYLLABLE CALCULATION (INTERNAL ONLY):\n"
        "- Count every vocalized vowel (A-E-I-O-U) as 1 syllable.\n"
        "- 'Init' (2), 'Dagat' (2), 'Araw' (2), 'Lupa' (2).\n"
        "- Do not provide a syllable count in your response. Output only the poem.\n\n"
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
        return {"reply": "Error: MISTRAL_API_KEY missing."}

    client = OpenAI(api_key=api_key, base_url="https://api.mistral.ai/v1")

    # ARCHITECTURAL NOTE: Removed the request for an audit in the user content.
    # This prevents the model from hallucinating counts and focuses it on the verse.
    messages = [
        {"role": "system", "content": get_tanaga_system_prompt()},
        {"role": "user", "content": f"Write a Tagalog Tanaga about: {safe_input}."}
    ]

    try:
        response = client.chat.completions.create(
            model="ministral-14b-latest", 
            messages=messages,
            temperature=0.1, # Deterministic setting to enforce structural rigidity.
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