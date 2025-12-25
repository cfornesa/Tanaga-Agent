"""
================================================================================
SYSTEM ARCHITECT: Chris Fornesa
PROJECT: Tanaga & Poetry Agent (Public Domain Edition)
MISSION: Balancing prosodic tradition with creative freedom.
GOVERNANCE: Local PII Redaction, User-Selected Rigor, Public Domain Clarity.
CONCEPTUAL FRAMEWORK: AI as a co-creator, not a replacement, for Philippine poetry.
================================================================================
"""

import os
import re
import gc
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional

# INITIALIZATION
app = FastAPI(title="Tanaga & Poetry Agent - Public Domain Edition")

# 1. CORS PROTOCOL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. PRIVACY SCRUBBER
def redact_pii(text: str) -> str:
    patterns = {
        "EMAIL": r'[\w\.-]+@[\w\.-]+\.\w+',
        "PHONE": r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}'
    }
    for label, pattern in patterns.items():
        text = re.sub(pattern, f"[{label}_REDACTED]", text, flags=re.IGNORECASE)
    return text

# 3. DYNAMIC SYSTEM PROMPT
def get_tanaga_system_prompt(strict: bool = False) -> str:
    rigor = "STRICT" if strict else "SUGGESTED"
    syllable_rule = "EXACTLY" if strict else "AIM FOR ~"
    return (
        f"You are an Expert Poet specialized in pre-colonial Philippine Tanaga.\n\n"
        f"GUIDELINES ({rigor}):\n"
        "1. LANGUAGE: Output ONLY ONE poem. No translation or explanation.\n"
        f"2. TAGALOG METER: {syllable_rule}7 syllables per line.\n"
        f"3. ENGLISH METER: {syllable_rule}8 syllables per line.\n"
        "4. WORD CHOICE: Prefer 1-3 syllable words, but prioritize emotional truth over rules.\n"
        "5. STRUCTURE: Exactly 4 lines of plain text. No markdown.\n"
        "6. CULTURAL DEPTH: Incorporate Filipino symbols/emotions (e.g., 'parol', 'sampaguita', 'damdamin').\n\n"
        "PHILOSOPHY: Prosodic purity is ideal, but the poem's soul matters more. "
        "Break rules if it serves the emotional core."
    )

# 4. PROSODY VALIDATOR (Simplified for Tagalog/English)
def validate_tanaga(poem: str, is_tagalog: bool) -> Dict:
    lines = poem.strip().split('\n')
    syllable_counts = []
    for line in lines:
        if is_tagalog:
            # Tagalog: Count vowels (approximation)
            count = len(re.findall(r'[aeiouáéíóú]', line.lower()))
        else:
            # English: Fallback to vowel counting
            count = len(re.findall(r'[aeiou]', line.lower()))
        syllable_counts.append(count)
    target = 7 if is_tagalog else 8
    is_valid = all(target - 1 <= count <= target + 1 for count in syllable_counts)  # ±1 syllable leeway
    return {"is_valid": is_valid, "counts": syllable_counts}

# 5. REQUEST MODEL
class PoetryRequest(BaseModel):
    user_input: str
    history: List[Dict] = []
    strict_meter: bool = False  # Default: Creative mode

# 6. HEALTH CHECK
@app.get("/")
async def health_check():
    return {
        "status": "online",
        "agent": "Tanaga Poet (Public Domain)",
        "features": ["creative_mode", "strict_mode", "prosody_validation"]
    }

# 7. MAIN ENDPOINT
@app.post("/generate-tanaga")
async def generate_tanaga(request: PoetryRequest):
    from openai import OpenAI
    import time

    # --- INPUT SANITIZATION ---
    safe_input = redact_pii(request.user_input)
    api_key = os.environ.get('MISTRAL_API_KEY')
    if not api_key:
        return {"error": "MISTRAL_API_KEY missing.", "status": 500}

    # --- LANGUAGE DETECTION ---
    user_query_lower = safe_input.lower()
    tagalog_triggers = ["tagalog", "sa tagalog", "filipino", "tag-alog", "wika"]
    is_tagalog = any(trigger in user_query_lower for trigger in tagalog_triggers)
    target_lang = "Tagalog" if is_tagalog else "English"
    meter = 7 if is_tagalog else 8

    # --- PROMPT ASSEMBLY ---
    messages = [
        {"role": "system", "content": get_tanaga_system_prompt(request.strict_meter)},
        {
            "role": "user",
            "content": (
                f"Write ONE {target_lang} Tanaga about: {safe_input}.\n"
                "Cultural note: If about diaspora/identity, use symbols like "
                "'bayan', 'lupa', 'gunita', or 'pagmimiss'."
            )
        }
    ]

    # --- GENERATION ---
    client = OpenAI(api_key=api_key, base_url="https://api.mistral.ai/v1")
    max_retries = 3 if request.strict_meter else 1
    last_error = None

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="ministral-14b-latest",
                messages=messages,
                temperature=0.3 if request.strict_meter else 0.5,
                max_tokens=100
            )
            reply_text = response.choices[0].message.content.strip()

            # --- VALIDATION ---
            validation = validate_tanaga(reply_text, is_tagalog)
            if not request.strict_meter or validation["is_valid"]:
                gc.collect()
                return {
                    "reply": reply_text,
                    "disclaimer": (
                        "AI-generated tanaga (public domain). May deviate from strict prosody. "
                        "For traditional use, human review is recommended."
                    ),
                    "prosody_check": validation,
                    "metadata": {
                        "language": target_lang,
                        "strict_mode": request.strict_meter,
                        "attempts": attempt + 1
                    }
                }

        except Exception as e:
            last_error = str(e)
            time.sleep(1)  # Avoid rate limits

    # --- FALLBACK ---
    gc.collect()
    return {
        "error": f"Generation failed after {max_retries} attempts. {last_error}",
        "status": 500
    }

# 8. LAUNCH
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
