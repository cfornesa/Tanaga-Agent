"""
================================================================================
SYSTEM ARCHITECT: Chris Fornesa
PROJECT: Tanaga & Poetry Agent (Polished Edition)
MISSION: Generating culturally resonant tanaga with optional prosodic polishing.
GOVERNANCE: Lightweight, stateless, and optimized for Replit deployment.
CONCEPTUAL FRAMEWORK: AI as a co-creator for Philippine poetic traditions.
================================================================================
"""

import os
import re
import gc
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional

# --- INITIALIZATION ---
app = FastAPI(title="Tanaga Poet API - Polished Edition")

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
def get_tanaga_system_prompt(strict: bool = False) -> str:
    """
    Generates dynamic system prompts based on meter strictness.
    Args:
        strict: Boolean for strict meter enforcement
    Returns:
        str: Formatted prompt for the LLM
    """
    rigor = "STRICT" if strict else "SUGGESTED"
    syllable_rule = "EXACTLY" if strict else "AIM FOR ~"
    return (
        f"You are an Expert Poet specialized in pre-colonial Philippine Tanaga.\n\n"
        f"GUIDELINES ({rigor}):\n"
        "1. LANGUAGE: Output ONLY ONE 4-line poem in plain text. No translation or explanation.\n"
        f"2. TAGALOG METER: {syllable_rule}7 syllables per line.\n"
        "   - Use contractions (e.g., 'nguni't' instead of 'ngunit').\n"
        "   - Drop optional words like 'ay' or 'aking' if needed.\n"
        "3. ENGLISH METER: AIM FOR ~8 syllables per line.\n"
        "4. WORD CHOICE: Prefer 1-3 syllable words. Prioritize emotional truth over rules.\n"
        "5. CULTURAL DEPTH: Use Filipino symbols (e.g., 'bayan', 'loob', 'hininga', 'damdam').\n"
        "6. DIASPORA THEMES: For identity/longing poems, incorporate:\n"
        "   - 'lupa'/ 'bayan' (homeland)\n"
        "   - 'gunita'/ 'alaala' (memory)\n"
        "   - 'pagmimiss'/ 'pananabik' (longing)\n\n"
        "PHILOSOPHY: Prosodic purity is ideal, but the poem's soul matters more."
    )

# --- 4. PROSODY VALIDATOR ---
def validate_tanaga(poem: str, is_tagalog: bool) -> Dict:
    """
    Validates syllable count for tanaga poems.
    Args:
        poem: Generated tanaga string
        is_tagalog: Boolean for Tagalog language processing
    Returns:
        dict: Validation results with syllable counts
    """
    lines = poem.strip().split('\n')
    syllable_counts = []
    for line in lines:
        # Count vowels (approximation for both Tagalog and English)
        count = len(re.findall(r'[aeiouáéíóú]', line.lower()))
        syllable_counts.append(count)
    target = 7 if is_tagalog else 8
    is_valid = all(target - 1 <= count <= target + 1 for count in syllable_counts)
    return {"is_valid": is_valid, "counts": syllable_counts}

# --- 5. TANGA POLISHER ---
def polish_tanaga(poem: str) -> str:
    """
    Applies rule-based polishing to Tagalog tanaga for strict meter.
    Focuses on common phrases that exceed syllable limits.
    Args:
        poem: Raw generated tanaga
    Returns:
        str: Polished tanaga with corrected meter
    """
    lines = poem.split('\n')
    replacements = {
        # General contractions
        "ngunit ": "nguni't ",
        "damdamin ay": "damdam ay",
        "sa aking ": "sa ",
        "sa bawat ": "sa ",
        # Diaspora/identity specific phrases
        "ngunit damdamin ay malaya": "nguni't damdam ay malaya",  # 9→7 syllables
        "sa pag-ibig sa bayan": "sa pag-ibig, bayan",            # 8→7 syllables
        "sa bawat hininga": "sa hininga'y",                      # 8→7 syllables
        "sa aking loob": "sa loob",                              # 7→6 (if needed)
        "sa tuwing ": "sa't ",                                   # 7→4 (context-dependent)
        "na walang nakita pa": "na di nakita pa",                # 7→6 syllables
        # Common verb phrases
        "ay nagmimiss": "'y nagmimiss",                          # 7→6 syllables
        "ay lumilipad": "'y lumilipad",                          # 7→6 syllables
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
    strict_meter: bool = False
    return_polished: bool = False  # New: Option to return only polished version

# --- 7. HEALTH CHECK ENDPOINT ---
@app.get("/")
async def health_check():
    """Endpoint for service status monitoring"""
    return {
        "status": "online",
        "agent": "Tanaga Poet API v2.1",
        "features": [
            "creative_mode (default)",
            "strict_meter_mode",
            "auto_polishing",
            "diaspora_optimized"
        ]
    }

# --- 8. MAIN GENERATION ENDPOINT ---
@app.post("/generate-tanaga")
async def generate_tanaga(request: PoetryRequest):
    """
    Core endpoint for tanaga generation.
    Handles:
    - Input sanitization
    - Language detection
    - LLM interaction
    - Prosody validation
    - Polishing (if needed)
    """
    from openai import OpenAI

    # Input processing
    safe_input = redact_pii(request.user_input)
    api_key = os.environ.get('MISTRAL_API_KEY')
    if not api_key:
        return {"error": "MISTRAL_API_KEY missing.", "status": 500}

    # Language detection
    user_query_lower = safe_input.lower()
    tagalog_triggers = ["tagalog", "sa tagalog", "filipino", "tag-alog", "wika"]
    is_tagalog = any(trigger in user_query_lower for trigger in tagalog_triggers)
    target_lang = "Tagalog" if is_tagalog else "English"

    # Prepare prompt
    messages = [
        {"role": "system", "content": get_tanaga_system_prompt(request.strict_meter)},
        {"role": "user", "content": f"Write ONE {target_lang} Tanaga about: {safe_input}."}
    ]

    # Generate with Mistral API
    client = OpenAI(api_key=api_key, base_url="https://api.mistral.ai/v1")
    try:
        response = client.chat.completions.create(
            model="ministral-14b-latest",
            messages=messages,
            temperature=0.3 if request.strict_meter else 0.5,
            max_tokens=100,
            timeout=10  # Prevent Replit timeouts
        )
        reply_text = response.choices[0].message.content.strip()

        # Validation and polishing
        validation = validate_tanaga(reply_text, is_tagalog)
        polished_text = None

        if is_tagalog and not validation["is_valid"]:
            polished_text = polish_tanaga(reply_text)
            polished_validation = validate_tanaga(polished_text, is_tagalog)
        else:
            polished_validation = None

        # Prepare response
        gc.collect()  # Clean up memory
        result = {
            "reply": reply_text,
            "prosody_check": validation,
            "disclaimer": (
                "AI-generated tanaga (public domain). "
                "For traditional use, human review recommended."
            ),
            "metadata": {
                "language": target_lang,
                "strict_mode": request.strict_meter,
                "tokens_used": getattr(response, 'usage', {}).get('total_tokens', None)
            }
        }

        # Include polished version if requested or if invalid meter
        if request.return_polished or (polished_text and polished_text != reply_text):
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
        timeout_keep_alive=30  # Prevent Replit timeouts
    )
