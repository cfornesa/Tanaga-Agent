"""
================================================================================
SYSTEM ARCHITECT: Chris Fornesa
PROJECT: Tanaga & Poetry Agent (Mistral Edition)
MISSION: Preserving Philippine poetic forms through structural and phonetic rigor.
GOVERNANCE: Local PII Redaction, Ethical Model Routing (Ministral 14B), Syllabic Anchoring.
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
app = FastAPI(title="Tanaga & Poetry Agent - Mistral Edition")

# 1. CORS PROTOCOL (The Digital Handshake)
# Enables secure communication between the Hostinger frontend and Replit backend.
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

# 3. POETIC PROTOCOL: THE GAIL FRAMEWORK
# CONCEPTUAL EXPLANATION: Combines pre-colonial Tagalog metrics with English adaptations.
# Focuses on 'Talinghaga' (evocative metaphor) and rigid syllabic counting.
def get_tanaga_system_prompt():
    return (
        "You are an Expert Poet specialized in the pre-colonial Philippine Tanaga.\n\n"
        "GOALS: Create structurally perfect 4-line poems with evocative metaphors.\n\n"
        "STRICT FORMATTING RULE:\n"
        "DO NOT USE MARKDOWN. No asterisks (*) or bolding. Output 4 lines only.\n\n"
        "CONCEPTUAL IMPLEMENTATION: SYLLABIC ANCHORING\n"
        "- For Tagalog: 4 lines, exactly 7 syllables per line.\n"
        "- For English: 4 lines, exactly 8 syllables per line.\n\n"
        "CONCEPTUAL IMPLEMENTATION: PHONETIC AUDIT\n"
        "- Count vocalized vowel sounds carefully (A-E-I-O-U).\n"
        "- 'Mga' counts as 2 syllables. 'Gabi'y' counts as 2.\n\n"
        "LANGUAGE: Expressive and evocative. Respond only in the language requested."
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
        "meter": "Hybrid-7/8",
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

    # CHOICE: Mistral AI prioritized for its low-carbon footprint and reasoning power.
    client = OpenAI(api_key=api_key, base_url="https://api.mistral.ai/v1")

    messages = [
        {"role": "system", "content": get_tanaga_system_prompt()},
        {"role": "user", "content": safe_input}
    ]

    try:
        # Utilizing Ministral 14B for precise vowel-count auditing.
        response = client.chat.completions.create(
            model="ministral-14b-latest", 
            messages=messages,
            # CONCEPTUAL IMPLEMENTATION: TEMPERATURE ANCHORING
            # 0.4 provides the 'Sweet Spot' for creative variety without losing meter.
            temperature=0.4, 
            max_tokens=200
        )

        reply_text = response.choices[0].message.content

        # STEP 6: Memory Cleanup (Ecological Conservation)
        del messages, safe_input
        gc.collect()

        return {"reply": reply_text.strip()}

    except Exception as e:
        gc.collect()
        return {"reply": f"System Error: {str(e)}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")