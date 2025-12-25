"""
================================================================================
SYSTEM ARCHITECT: Christopher Fornesa
PROJECT: Tanaga & Poetry Agent (Final Production Edition)
MISSION: Generate culturally authentic Tagalog tanaga with optional strict meter enforcement
GOVERNANCE: Minimal intervention, pattern-specific polishing, and full transparency
CONCEPTUAL FRAMEWORK: AI as a cultural co-creator with human-in-the-loop refinement
================================================================================
"""

import os
import re
import gc
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Tuple

# --- INITIALIZATION ---
app = FastAPI(
    title="Tanaga Poet API",
    description="Generates traditional Philippine tanaga poetry with optional meter polishing",
    version="4.0"
)

# --- 1. CORS MIDDLEWARE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. PRIVACY UTILITY ---
def redact_pii(text: str) -> str:
    """Redacts personally identifiable information from user inputs."""
    patterns = {
        "EMAIL": r'[\w\.-]+@[\w\.-]+\.\w+',
        "PHONE": r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}'
    }
    for label, pattern in patterns.items():
        text = re.sub(pattern, f"[{label}_REDACTED]", text, flags=re.IGNORECASE)
    return text

# --- 3. SYSTEM PROMPT GENERATOR ---
def get_tanaga_system_prompt() -> str:
    """Generates optimized system prompt for Tagalog tanaga generation."""
    return (
        "You are an Expert Poet specialized in pre-colonial Philippine Tanaga.\n\n"
        "GUIDELINES:\n"
        "1. Output ONLY ONE 4-line poem in plain Tagalog. No translation or explanation.\n"
        "2. Meter: Aim for approximately 7 syllables per line, but prioritize natural flow.\n"
        "3. For diaspora themes, incorporate:\n"
        "   - 'bayan' (homeland)\n"
        "   - 'loob' (inner self)\n"
        "   - 'gunita' (memory)\n"
        "   - 'damdamin/damdam' (feelings)\n"
        "4. Use simple, evocative language. Avoid overused metaphors.\n"
        "5. Structure: Exactly 4 lines, no markdown, no asterisks.\n"
        "6. When writing about identity/longing, focus on emotional truth.\n"
        "7. Common patterns to consider:\n"
        "   - 'Lupang walang nakita' (unseen homeland)\n"
        "   - 'Damdamin ko'y...' (my feelings...)\n"
        "   - 'Sa pag-ibig sa bayan' (love for homeland)"
    )

# --- 4. SYLLABLE COUNTER ---
def count_syllables(line: str) -> int:
    """Counts syllables in a Tagalog line using vowel counting."""
    return len(re.findall(r'[aeiouáéíóú]', line.lower()))

# --- 5. ENHANCED TANGA POLISHER ---
def polish_tanaga(poem: str) -> Tuple[str, List[Dict]]:
    """
    Applies targeted polishing to Tagalog tanaga for strict meter compliance.
    Handles specific patterns found in diaspora-themed poetry.
    """
    lines = poem.split('\n')
    polished_lines = []
    changes = []

    for i, line in enumerate(lines):
        original_line = line
        current_line = line

        # Rule 1: Possessive contractions
        if "ko'y " in current_line:
            current_line = current_line.replace("ko'y ", "'y ")
            changes.append({
                "line": i+1,
                "original": original_line,
                "change": "possessive_contraction",
                "polished": current_line
            })

        if "mo'y " in current_line:
            current_line = current_line.replace("mo'y ", "'y ")

        # Rule 2: Repetitive structures
        if current_line.count("walang") > 1:
            parts = current_line.split("walang")
            current_line = f"walang{parts[1]}".strip()
            changes.append({
                "line": i+1,
                "original": original_line,
                "change": "repetitive_structure",
                "polished": current_line
            })

        # Rule 3: Common phrase replacements
        replacements = {
            "damdamin ko'y malaya": ("damdam ko'y malaya", "emotional_phrase"),
            "damdamin'y Pilipino": ("damdam ay Pilipino", "descriptive_phrase"),
            "walang bayan, walang lupa": ("walang bayan, di lupa", "repetitive_structure"),
            "sa damdamin ko'y": ("sa damdam ko'y", "possessive_contraction"),
            "ngunit damdamin'y": ("nguni't damdam ay", "conjunction_phrase"),
            "sa damdamin": ("sa damdam", "emotional_phrase"),
        }

        for old, (new, change_type) in replacements.items():
            if old in current_line and old != new:
                current_line = current_line.replace(old, new)
                changes.append({
                    "line": i+1,
                    "original": original_line if old in original_line else current_line,
                    "change": change_type,
                    "polished": current_line
                })

        # Rule 4: Final syllable check and adjustments
        syllable_count = count_syllables(current_line)
        if syllable_count > 8:
            if "malaya" in current_line:
                current_line = current_line.replace("malaya", "layà")
            elif "Pilipino" in current_line and "damdam" not in current_line:
                current_line = current_line.replace("Pilipino", "Pinoy")

        polished_lines.append(current_line)

    return '\n'.join(polished_lines), changes

# --- 6. PROSODY VALIDATOR ---
def validate_tanaga(poem: str) -> Dict:
    """Validates syllable count for each line in a tanaga."""
    lines = poem.strip().split('\n')
    syllable_counts = []
    for line in lines:
        syllable_counts.append(count_syllables(line))
    return {
        "is_valid": all(6 <= count <= 8 for count in syllable_counts),
        "counts": syllable_counts,
        "total_syllables": sum(syllable_counts)
    }

# --- 7. REQUEST MODEL ---
class PoetryRequest(BaseModel):
    user_input: str
    history: List[Dict] = []
    strict_meter: bool = False
    meter_tolerance: int = 1
    max_polish_pass: int = 3

# --- 8. HEALTH CHECK ENDPOINT ---
@app.get("/")
async def health_check():
    """Endpoint for service status monitoring"""
    return {
        "status": "online",
        "agent": "Tanaga Poet API v4.0",
        "features": [
            "emotional_resonance_priority",
            "strict_meter_option",
            "pattern_specific_polishing",
            "change_tracking"
        ]
    }

# --- 9. MAIN GENERATION ENDPOINT ---
@app.post("/generate-tanaga")
async def generate_tanaga(request: PoetryRequest):
    """Core endpoint for tanaga generation with optional polishing."""
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

    if not is_tagalog:
        return {"error": "Currently optimized for Tagalog input only.", "status": 400}

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
            temperature=0.1,
            max_tokens=100,
            timeout=10
        )

        reply_text = response.choices[0].message.content.strip()

        # Get token usage safely
        tokens_used = None
        if hasattr(response, 'usage') and response.usage:
            tokens_used = response.usage.total_tokens

        # Initial validation
        validation = validate_tanaga(reply_text)
        polished_text = reply_text
        all_changes = []

        # Polishing loop for strict meter
        if request.strict_meter:
            for _ in range(request.max_polish_pass):
                polished_text, changes = polish_tanaga(polished_text)
                if changes:
                    all_changes.extend(changes)
                validation = validate_tanaga(polished_text)

                # Stop if valid or no more changes
                if (validation["is_valid"] or
                    all(count <= 7 + request.meter_tolerance for count in validation["counts"])):
                    break

        # Final validation
        final_validation = validate_tanaga(polished_text)

        # Prepare response
        gc.collect()
        result = {
            "reply": reply_text,
            "prosody_check": validate_tanaga(reply_text),
            "disclaimer": (
                "AI-generated tanaga (public domain). "
                "For traditional use, human review recommended."
            ),
            "metadata": {
                "language": "Tagalog",
                "strict_mode": request.strict_meter,
                "meter_tolerance": request.meter_tolerance,
                "tokens_used": tokens_used
            }
        }

        # Include polished version if different
        if polished_text != reply_text:
            result["polished_reply"] = polished_text
            result["polished_check"] = final_validation
            result["changes_made"] = all_changes

        return result

    except Exception as e:
        gc.collect()
        return {"error": f"Generation failed: {str(e)}", "status": 500}

# --- 10. LAUNCH CONFIGURATION ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        timeout_keep_alive=30
    )
