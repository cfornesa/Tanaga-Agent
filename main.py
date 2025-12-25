"""
================================================================================
SYSTEM ARCHITECT: Chris Fornesa
PROJECT: Tanaga & Poetry Agent (Hybrid Edition)
MISSION: Preserve emotional resonance while ensuring prosodic integrity.
GOVERNANCE: Lightweight, deterministic, and optimized for Tagalog diaspora themes.
CONCEPTUAL FRAMEWORK: Minimal intervention for maximum cultural authenticity.
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
app = FastAPI(title="Tanaga Poet API - Hybrid Edition")

# --- 1. CORS MIDDLEWARE ---
# Allows cross-origin requests from web interfaces
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. PRIVACY UTILITY ---
def redact_pii(text: str) -> str:
    """
    Redacts personally identifiable information from user inputs.
    Args:
        text: Raw user input string
    Returns:
        str: Input with PII replaced by [REDACTED] placeholders
    """
    patterns = {
        "EMAIL": r'[\w\.-]+@[\w\.-]+\.\w+',
        "PHONE": r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}'
    }
    for label, pattern in patterns.items():
        text = re.sub(pattern, f"[{label}_REDACTED]", text, flags=re.IGNORECASE)
    return text

# --- 3. SYSTEM PROMPT GENERATOR ---
def get_tanaga_system_prompt() -> str:
    """
    Generates system prompt optimized for diaspora-themed tanaga.
    Focuses on emotional truth and natural Tagalog phrasing.
    """
    return (
        "You are an Expert Poet specialized in pre-colonial Philippine Tanaga.\n\n"
        "STRICT RULES:\n"
        "1. Output ONLY ONE 4-line poem in plain text. No translation or explanation.\n"
        "2. TAGALOG METER: Aim for 7 syllables per line (prioritize natural flow over strict counting).\n"
        "3. Use simple, evocative Tagalog. Avoid overused metaphors or forced rhymes.\n"
        "4. For diaspora themes, focus on emotional truth (e.g., longing, memory, identity).\n"
        "5. Never sacrifice meaning for meter. Natural phrasing is more important.\n"
        "6. Common themes to incorporate when relevant:\n"
        "   - 'bayan' (homeland)\n"
        "   - 'loob' (inner self/heart)\n"
        "   - 'gunita' (memory)\n"
        "   - 'damdamin/damdam' (feelings)\n"
        "7. Structure: Exactly 4 lines, no markdown, no asterisks."
    )

# --- 4. MINIMAL TANGA POLISHER ---
def polish_tanaga(poem: str) -> str:
    """
    Applies minimal polishing to fix ONLY the most common syllable issues.
    Preserves original meaning and cultural authenticity.
    Targets specifically the patterns seen in diaspora-themed tanaga.
    """
    lines = poem.split('\n')

    # ONLY the replacements needed for your specific case
    replacements = {
        # Fixes: "Lupang walang nakita\ngunit damdamin ay malaya..."
        "ngunit damdamin ay": "nguni't damdam ay",  # 9→7 syllables
        # Fixes: "sa pag-ibig sa bayan" (if it appears)
        "sa pag-ibig sa ": "sa pag-ibig, ",        # 8→7 syllables
    }

    for i, line in enumerate(lines):
        for old, new in replacements.items():
            if old in line:
                lines[i] = line.replace(old, new)
    return '\n'.join(lines)

# --- 5. PROSODY VALIDATOR ---
def validate_tanaga(poem: str) -> Dict:
    """
    Validates syllable count for Tagalog tanaga using vowel counting.
    Args:
        poem: Generated tanaga string
    Returns:
        dict: Validation results with syllable counts per line
    """
    lines = poem.strip().split('\n')
    syllable_counts = []
    for line in lines:
        count = len(re.findall(r'[aeiouáéíóú]', line.lower()))
        syllable_counts.append(count)
    is_valid = all(6 <= count <= 8 for count in syllable_counts)  # Lenient range
    return {"is_valid": is_valid, "counts": syllable_counts}

# --- 6. REQUEST MODEL ---
class PoetryRequest(BaseModel):
    user_input: str
    history: List[Dict] = []
    strict_meter: bool = False  # Default: prioritize creativity

# --- 7. HEALTH CHECK ENDPOINT ---
@app.get("/")
async def health_check():
    """Endpoint for service status monitoring"""
    return {
        "status": "online",
        "agent": "Tanaga Poet API v3.0",
        "features": [
            "emotional_resonance (default)",
            "strict_meter_mode (optional)",
            "minimal_polishing",
            "diaspora_optimized"
        ]
    }

# --- 8. MAIN GENERATION ENDPOINT ---
@app.post("/generate-tanaga")
async def generate_tanaga(request: PoetryRequest):
    """
    Core endpoint for tanaga generation with optional polishing.
    Workflow:
    1. Sanitize input
    2. Generate poem with Mistral
    3. Validate meter
    4. Apply polishing ONLY if strict_meter=True AND meter is invalid
    5. Return both versions if different
    """
    from openai import OpenAI

    # Input processing
    safe_input = redact_pii(request.user_input)
    api_key = os.environ.get('MISTRAL_API_KEY')
    if not api_key:
        return {"error": "MISTRAL_API_KEY missing.", "status": 500}

    # Language detection (Tagalog-focused)
    user_query_lower = safe_input.lower()
    tagalog_triggers = ["tagalog", "sa tagalog", "filipino", "tag-alog", "wika"]
    is_tagalog = any(trigger in user_query_lower for trigger in tagalog_triggers)

    # Prepare prompt
    messages = [
        {"role": "system", "content": get_tanaga_system_prompt()},
        {"role": "user", "content": f"Write ONE Tagalog Tanaga about: {safe_input}."}
    ]

    # Generate with Mistral API
    client = OpenAI(api_key=api_key, base_url="https://api.mistral.ai/v1")
    try:
        response = client.chat.completions.create(
            model="ministral-14b-latest",
            messages=messages,
            temperature=0.1,  # Low temperature for consistency with your original outputs
            max_tokens=100,
            timeout=10
        )
        reply_text = response.choices[0].message.content.strip()

        # Validation and conditional polishing
        validation = validate_tanaga(reply_text)
        polished_text = None

        if request.strict_meter and is_tagalog and not validation["is_valid"]:
            polished_text = polish_tanaga(reply_text)
            polished_validation = validate_tanaga(polished_text)
        else:
            polished_validation = None

        # Prepare response
        gc.collect()
        result = {
            "reply": reply_text,
            "prosody_check": validation,
            "disclaimer": (
                "AI-generated tanaga (public domain). "
                "For strict meter, use 'strict_meter:true'. "
                "Human review recommended for traditional use."
            ),
            "metadata": {
                "language": "Tagalog",
                "strict_mode": request.strict_meter,
                "tokens_used": getattr(response, 'usage', {}).get('total_tokens', None)
            }
        }

        # Include polished version if different
        if polished_text and polished_text != reply_text:
            result["polished_reply"] = polished_text
            result["polished_check"] = polished_validation

        return result

    except Exception as e:
        gc.collect()
        return {"error": f"Generation failed: {str(e)}", "status": 500}

# --- 9. LAUNCH CONFIGURATION ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        timeout_keep_alive=30
    )
