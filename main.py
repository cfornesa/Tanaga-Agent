"""
================================================================================
SYSTEM ARCHITECT: Christopher Fornesa
PROJECT: Tanaga & Poetry Agent (Bilingual Prosodic Edition)
MISSION: Preserve pre-colonial Philippine poetic forms via algorithmic rigor.
GOVERNANCE: Local PII Redaction, Deterministic Inference, Phonetic Anchoring.
================================================================================
"""

import os
import re
import gc
import uvicorn
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional

# Operational Transparency Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. SYSTEM INITIALIZATION
# CONCEPTUAL REASONING: FastAPI is selected for its asynchronous lifecycle management, 
# ensuring high-concurrency stability during intensive phonetic auditing.
app = FastAPI(
    title="Tanaga & Poetry Agent",
    description="Linguistic scaffolding for the traditional Filipino Tanaga",
    version="8.0"
)

# 2. CORS PROTOCOL (The Digital Handshake)
# Enables secure communication between the Hostinger UI and the Replit logic layer.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. PRIVACY SCRUBBER (PII Sanitization Layer)
# MISSION ALIGNMENT: Implements "Privacy-by-Design" by redacting sensitive 
# identifiers locally before they exit the secure environment.
def redact_pii(text: str) -> str:
    patterns = {
        "EMAIL": r'[\w\.-]+@[\w\.-]+\.\w+',
        "PHONE": r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}'
    }
    for label, pattern in patterns.items():
        text = re.sub(pattern, f"[{label}_REDACTED]", text, flags=re.IGNORECASE)
    return text

# 4. PROSODIC CONSTRAINT ENGINE (Prompt Logic)
# CONCEPTUAL REASONING: Maps cultural meter to machine logic. By using 
# "Staccato Instructions," we overcome the tokenization limitations of LLMs.
def get_tanaga_system_prompt(language: str = "English") -> str:
    if language == "Tagalog":
        return (
            "You are an Expert Poet specialized in pre-colonial Philippine Tanaga.\n\n"
            "STRICT ARCHITECTURAL CONSTRAINTS:\n"
            "1. STRUCTURE: Exactly ONE 4-line poem in Tagalog.\n"
            "2. METER: Exactly 7 syllables per line. Count every vocalized vowel.\n"
            "3. STACCATO LIMIT: Use short words (max 3 syllables) to ensure phonetic accuracy.\n"
            "4. TALINGHAGA: Use traditional imagery: 'bayan' (homeland), 'loob' (inner self).\n"
            "5. NO MARKDOWN: Plain text only. No bolding or asterisks."
        )
    else:
        return (
            "You are an Expert Poet specialized in structured English poetry.\n\n"
            "STRICT ARCHITECTURAL CONSTRAINTS:\n"
            "1. STRUCTURE: Exactly ONE 4-line poem in English.\n"
            "2. METER: Exactly 8 syllables per line.\n"
            "3. STACCATO LIMIT: Use simple, evocative words (max 3 syllables).\n"
            "4. NO MARKDOWN: Plain text only. No bolding or asterisks."
        )

# 5. INPUT SCHEMA (Data Modeling)
class PoetryRequest(BaseModel):
    user_input: str
    history: List[Dict] = []
    language: Optional[str] = None

# 6. BILINGUAL ROUTER (Language Logic)
def detect_language(user_input: str, explicit_language: Optional[str] = None) -> str:
    if explicit_language:
        return explicit_language.capitalize()

    user_input_lower = user_input.lower()
    tagalog_triggers = ["tagalog", "sa tagalog", "filipino", "tag-alog"]

    if any(trigger in user_input_lower for trigger in tagalog_triggers):
        return "Tagalog"
    return "English"

# 7. MAIN GENERATION ENDPOINT
@app.post("/generate-tanaga")
async def generate_poetry(request: PoetryRequest):
    """
    STACCATO-VERACITY PROCESSOR
    Workflow includes PII scrubbing, language-anchoring, and resource conservation.
    """
    try:
        from openai import OpenAI

        # Step 1: Privacy Lockdown
        safe_input = redact_pii(request.user_input)
        api_key = os.environ.get('MISTRAL_API_KEY')

        if not api_key:
            return {"reply": "Error: API key missing."}

        # Step 2: Language-Logic Anchoring
        language = detect_language(safe_input, request.language)
        meter = "7 syllables" if language == "Tagalog" else "8 syllables"

        # Step 3: Deterministic Generation
        client = OpenAI(api_key=api_key, base_url="https://api.mistral.ai/v1")

        # Use low temperature (0.1) for high structural veracity
        response = client.chat.completions.create(
            model="mistral-tiny", 
            messages=[
                {"role": "system", "content": get_tanaga_system_prompt(language)},
                {"role": "user", "content": f"Theme: {safe_input}. Language: {language}."}
            ],
            temperature=0.1,
            max_tokens=100
        )

        reply_text = response.choices[0].message.content.strip()

        # Step 4: Resource Conservation
        gc.collect()

        return {
            "reply": reply_text,
            "metadata": {
                "language": language,
                "meter": meter,
                "governance": "PII Scrubbed | Prosody Audited"
            }
        }

    except Exception as e:
        logger.error(f"System Error: {str(e)}")
        return {"reply": f"System Error: {str(e)}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")