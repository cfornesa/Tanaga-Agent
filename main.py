"""
================================================================================
SYSTEM ARCHITECT: Chris Fornesa
PROJECT: Tanaga & Poetry Agent (Veracity Edition)
MISSION: Preserving Philippine poetic forms through rigid syllabic auditing.
GOVERNANCE: Local PII Redaction, Ethical Model Routing, Syllabic Stress-Testing.
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
# CONCEPTUAL EXPLANATION: Configures Cross-Origin Resource Sharing to allow 
# secure data exchange between the Hostinger frontend and the Replit API.
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

# 3. POETIC PROTOCOL: REINFORCED GAIL FRAMEWORK
# CONCEPTUAL EXPLANATION: Combines pre-colonial Tagalog metrics with English adaptations.
# ARCHITECTURAL NOTE: Transitioned to "Stress-Test" logic to mitigate LLM token-counting errors.
def get_tanaga_system_prompt():
    return (
        "You are an Expert Poet specialized in the pre-colonial Philippine Tanaga.\n\n"
        "STRICT ARCHITECTURAL CONSTRAINTS:\n"
        "1. TAGALOG METER: Exactly 7 syllables per line. (A-A-A-A or A-B-A-B).\n"
        "2. ENGLISH METER: Exactly 8 syllables per line. (A-A-A-A or A-B-A-B).\n"
        "3. STRUCTURE: Exactly 4 lines total.\n"
        "4. NO MARKDOWN: Plain text only. No asterisks (*). No bolding.\n\n"
        "SYLLABLE AUDIT METHOD (INTERNAL STRESS-TEST):\n"
        "- Break every word into its vocalized vowel sounds (A-E-I-O-U) before outputting.\n"
        "- Tagalog Example (7): Ang pa-lay ay la-mi-gas.\n"
        "- English Example (8): The sun is hot up-on the sand.\n"
        "- Avoid 'mga' or complex diphthongs that confuse tokenization.\n\n"
        "TONE: High-density metaphor (Talinghaga). Professional and structurally rigid."
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
        "meter": "Fixed-7/8-Audit",
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

    # ARCHITECTURAL NOTE: Prompting the model to specifically perform a count in its response phase.
    messages = [
        {"role": "system", "content": get_tanaga_system_prompt()},
        {"role": "user", "content": f"Theme: {safe_input}. Construct the verse. Audit syllable counts for each line to ensure strict adherence."}
    ]

    try:
        # Utilizing Ministral 14B for precise vowel-count auditing.
        response = client.chat.completions.create(
            model="ministral-14b-latest", 
            messages=messages,
            # CONCEPTUAL IMPLEMENTATION: TEMPERATURE ANCHORING
            # Lowered to 0.15 to prioritize structural veracity over creative drift.
            temperature=0.15, 
            max_tokens=300
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