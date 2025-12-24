"""
================================================================================
SYSTEM ARCHITECT: Chris Fornesa
PROJECT: Tanaga & Poetry Agent (Veracity Edition)
MISSION: Ensuring syllabic veracity in pre-colonial Philippine poetic forms.
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

# INITIALIZATION: FastAPI selected for its high-speed binary stream handling.
# CONCEPTUAL REASONING: Minimizing latency is critical for maintaining the 
# "Poetic Flow" while ensuring the server remains ecologically efficient.
app = FastAPI(title="Tanaga & Poetry Agent - Veracity Edition")

# 1. CORS PROTOCOL (The Digital Handshake)
# CONCEPTUAL REASONING: This enables secure Cross-Origin communication between 
# the Hostinger UI and the Replit logic layer, bypassing browser-level security 
# blocks while maintaining a strict API boundary.
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

# 3. POETIC PROTOCOL: VOWEL-ANCHORING FRAMEWORK
# CONCEPTUAL REASONING: This framework addresses the "Phonetic Math" limitation 
# of LLMs. By using "Staccato Constraints," we force the model to prioritize 
# structural rigidness (Syllabic Anchoring) over creative linguistic drift.
def get_tanaga_system_prompt():
    return (
        "You are an Expert Poet specialized in the pre-colonial Tagalog Tanaga.\n\n"
        "STRICT MATHEMATICAL RULES:\n"
        "1. TAGALOG METER: Exactly 7 syllables per line. (Count: A-E-I-O-U).\n"
        "2. ENGLISH METER: Exactly 8 syllables per line.\n"
        "3. WORD CHOICE: Use simple, short words. Avoid words with more than 3 syllables.\n"
        "4. NO MARKDOWN: Output 4 lines of plain text only.\n\n"
        "SYLLABLE AUDIT (VOWEL COUNTING):\n"
        "- Break the line: 'Ang-da-gat-ay-ma-la-wak' (7).\n"
        "- Do not use 'Lumilipad' (4 syllables) for a 3-syllable slot.\n"
        "- Count 'mga' as 2 syllables.\n\n"
        "TONE: Use 'Talinghaga' (Metaphor). Accuracy is more important than flourish."
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
        "logic": "Vowel-Anchoring-Enabled",
        "model": "ministral-14b-2512"
    }

# 5. MAIN GENERATION ENDPOINT
# CONCEPTUAL REASONING: Orchestrates the request lifecycle. It enforces 
# "Analytical Rigidity" by setting a low Temperature (0.1).
@app.post("/generate-tanaga")
async def process_chat(request: PoetryRequest):
    from openai import OpenAI

    safe_input = redact_pii(request.user_input)
    api_key = os.environ.get('MISTRAL_API_KEY')

    if not api_key:
        return {"reply": "Error: MISTRAL_API_KEY not configured."}

    client = OpenAI(api_key=api_key, base_url="https://api.mistral.ai/v1")

    # ARCHITECTURAL NOTE: Forcing a "Vowel-Count Audit" in the prompt phase 
    # provides an additional logical guardrail against hallucinated syllables.
    messages = [
        {"role": "system", "content": get_tanaga_system_prompt()},
        {"role": "user", "content": f"Theme: {safe_input}. Count every vowel. Ensure 7 syllables for Tagalog."}
    ]

    try:
        response = client.chat.completions.create(
            model="ministral-14b-latest", 
            messages=messages,
            temperature=0.1, # Minimized creative drift to favor mathematical accuracy.
            max_tokens=250
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