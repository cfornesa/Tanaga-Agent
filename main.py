"""
================================================================================
SYSTEM ARCHITECT: Chris Fornesa
PROJECT: Tanaga & Poetry Agent (Optimized for Replit)
MISSION: Balancing prosodic tradition, creative freedom, and compute efficiency.
GOVERNANCE: Local PII Redaction, User-Selected Rigor, Minimal Retries.
CONCEPTUAL FRAMEWORK: Lightweight, stateless, and Replit-friendly.
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

# --- INITIALIZATION ---
app = FastAPI(title="Tanaga & Poetry Agent - Replit Optimized")

# --- 1. CORS PROTOCOL ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. PRIVACY SCRUBBER ---
def redact_pii(text: str) -> str:
    patterns = {
        "EMAIL": r'[\w\.-]+@[\w\.-]+\.\w+',
        "PHONE": r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}'
    }
    for label, pattern in patterns.items():
        text = re.sub(pattern, f"[{label}_REDACTED]", text, flags=re.IGNORECASE)
    return text

# --- 3. DYNAMIC SYSTEM PROMPT (Tagalog-Optimized) ---
def get_tanaga_system_prompt(strict: bool = False) -> str:
    rigor = "STRICT" if strict else "SUGGESTED"
    syllable_rule = "EXACTLY" if strict else "AIM FOR ~"
    return (
        f"You are an Expert Poet specialized in pre-colonial Philippine Tanaga.\n\n"
        f"GUIDELINES ({rigor}):\n"
        "1. LANGUAGE: Output ONLY ONE 4-line poem in plain text. No translation or explanation.\n"
        f"2. TAGALOG METER: {syllable_rule}7 syllables per line.\n"
        "   - Use contractions (e.g., 'nguni’t' instead of 'ngunit').\n"
        "   - Drop optional words like 'ay' or 'aking' if needed.\n"
        "3. ENGLISH METER: AIM FOR ~8 syllables per line.\n"
        "4. WORD CHOICE: Prefer 1-3 syllable words. Prioritize emotional truth over rules.\n"
        "5. CULTURAL DEPTH: Use Filipino symbols (e.g., 'bayan', 'loob', 'hininga', 'damdam').\n\n"
        "PHILOSOPHY: Prosodic purity is ideal, but the poem's soul matters more."
    )

# --- 4. PROSODY VALIDATOR (Lightweight) ---
def validate_tanaga(poem: str, is_tagalog: bool) -> Dict:
    lines = poem.strip().split('\n')
    syllable_counts = []
    for line in lines:
        # Count vowels (works for Tagalog/English approximation)
        count = len(re.findall(r'[aeiouáéíóú]', line.lower()))
        syllable_counts.append(count)
    target = 7 if is_tagalog else 8
    is_valid = all(target - 1 <= count <= target + 1 for count in syllable_counts)
    return {"is_valid": is_valid, "counts": syllable_counts}

# --- 5. TANGA POLISHER (Tagalog-Specific) ---
def polish_tanaga(poem: str) -> str:
    lines = poem.split('\n')
    replacements = {
        "damdamin ay": "damdam ay",    # 8 → 7 syllables
        "sa bawat hininga": "sa hininga’y",  # 8 → 7
        "sa aking loob": "sa loob",    # 8 → 7
        "ngunit ": "nguni’t ",         # 6 → 5 (contraction)
    }
    polished_lines = []
    for line in lines:
        for old, new in replacements.items():
            if old in line:
                line = line.replace(old, new)
        polished_lines.append(line)
    return '\n'.join(polished_lines)

# --- 6. REQUEST MODEL ---
class PoetryRequest(BaseModel):
    user_input: str
    history: List[Dict] = []
    strict_meter: bool = False  # Default: Creative mode

# --- 7. HEALTH CHECK ---
@app.get("/")
async def health_check():
    return {
        "status": "online",
        "agent": "Tanaga Poet (Replit Optimized)",
        "features": ["creative_mode", "strict_mode", "auto_polish"]
    }

# --- 8. MAIN ENDPOINT (Compute-Optimized) ---
@app.post("/generate-tanaga")
async def generate_tanaga(request: PoetryRequest):
    from openai import OpenAI

    # --- Input Sanitization ---
    safe_input = redact_pii(request.user_input)
    api_key = os.environ.get('MISTRAL_API_KEY')
    if not api_key:
        return {"error": "MISTRAL_API_KEY missing.", "status": 500}

    # --- Language Detection ---
    user_query_lower = safe_input.lower()
    tagalog_triggers = ["tagalog", "sa tagalog", "filipino", "tag-alog", "wika"]
    is_tagalog = any(trigger in user_query_lower for trigger in tagalog_triggers)
    target_lang = "Tagalog" if is_tagalog else "English"

    # --- Prompt Assembly ---
    messages = [
        {"role": "system", "content": get_tanaga_system_prompt(request.strict_meter)},
        {"role": "user", "content": f"Write ONE {target_lang} Tanaga about: {safe_input}."}
    ]

    # --- Generation (Single Attempt for Replit) ---
    client = OpenAI(api_key=api_key, base_url="https://api.mistral.ai/v1")
    try:
        response = client.chat.completions.create(
            model="ministral-14b-latest",
            messages=messages,
            temperature=0.3 if request.strict_meter else 0.5,
            max_tokens=100,
            timeout=10  # Fail fast on Replit
        )
        reply_text = response.choices[0].message.content.strip()

        # --- Post-Processing ---
        validation = validate_tanaga(reply_text, is_tagalog)
        polished_text = polish_tanaga(reply_text) if is_tagalog and not validation["is_valid"] else reply_text
        polished_validation = validate_tanaga(polished_text, is_tagalog) if is_tagalog else validation

        # --- Response ---
        gc.collect()  # Free memory
        return {
            "reply": reply_text,
            "polished_reply": polished_text if polished_text != reply_text else None,
            "prosody_check": validation,
            "polished_check": polished_validation if polished_text != reply_text else None,
            "disclaimer": (
                "AI-generated tanaga (public domain). For strict meter, use 'strict_meter:true'. "
                "Human review recommended for traditional use."
            ),
            "metadata": {
                "language": target_lang,
                "strict_mode": request.strict_meter,
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else None
            }
        }

    except Exception as e:
        gc.collect()
        return {"error": f"Generation failed: {str(e)}", "status": 500}

# --- 9. LAUNCH (Replit-Compatible) ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info", timeout_keep_alive=30)
