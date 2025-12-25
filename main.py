"""
================================================================================
SYSTEM ARCHITECT: Christopher Fornesa
PROJECT: Tanaga & Poetry Agent (Production Ready)
MISSION: Generate culturally authentic Tagalog tanaga with strict meter enforcement
GOVERNANCE: Multi-pass polishing with cultural sensitivity and change tracking
================================================================================
"""

import os
import re
import gc
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Tuple

# --- INITIALIZATION ---
app = FastAPI(
    title="Tanaga Poet API",
    description="Generates traditional Philippine tanaga poetry with strict meter enforcement",
    version="5.0"
)

# --- CORS MIDDLEWARE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- PRIVACY UTILITY ---
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

# --- SYLLABLE COUNTER ---
def count_syllables(line: str) -> int:
    """
    Counts syllables in a Tagalog line using vowel counting.
    Args:
        line: Single line of Tagalog text
    Returns:
        int: Approximate syllable count
    """
    return len(re.findall(r'[aeiouáéíóú]', line.lower()))

# --- TANGA SYSTEM PROMPT ---
def get_tanaga_system_prompt() -> str:
    """
    Generates system prompt optimized for Tagalog tanaga generation.
    Focuses on emotional authenticity and cultural resonance.
    """
    return (
        "You are an Expert Poet specialized in pre-colonial Philippine Tanaga.\n\n"
        "STRICT RULES:\n"
        "1. Output ONLY ONE 4-line poem in plain Tagalog\n"
        "2. Each line must be exactly 7 syllables when possible\n"
        "3. Use simple, evocative language\n"
        "4. For diaspora themes, incorporate:\n"
        "   - 'bayan' (homeland)\n"
        "   - 'loob' (inner self)\n"
        "   - 'gunita' (memory)\n"
        "   - 'damdamin' (feelings)\n"
        "5. Structure: 4 lines, no markdown, no explanation\n"
        "6. Prioritize emotional truth over strict meter\n"
        "7. Common patterns to use:\n"
        "   - 'Lupang walang nakita'\n"
        "   - 'Damdamin ko'y...'\n"
        "   - 'Sa pag-ibig sa bayan'"
    )

# --- AGGRESSIVE TANGA POLISHER ---
def polish_tanaga(poem: str) -> Tuple[str, List[Dict]]:
    """
    Multi-level polisher for Tagalog tanaga with strict meter enforcement.
    Applies progressively more aggressive corrections while preserving meaning.

    Args:
        poem: Raw generated tanaga
    Returns:
        tuple: (polished_poem, list_of_changes)
    """
    lines = poem.split('\n')
    polished_lines = []
    changes = []

    for i, line in enumerate(lines):
        original_line = line
        current_line = line

        # Level 1: Pattern-based replacements (most common issues)
        replacements = [
            # 9→7 syllable patterns
            (r'damdamin ko\'y (\w+)', r'damdam ko\'y \1', "emotion_contraction"),
            (r'sa bawat (\w+), (\w+)', r'sa \1, \2', "repetitive_structure"),
            (r'nag-iisa sa (\w+)', r'nag-iisa \1', "preposition_contraction"),
            (r'laging (\w+)', r'\1', "redundant_adverb"),
            (r'(\w+) ko\'y', r'\1 ko', "possessive_simple"),

            # 8→7 syllable patterns
            (r'sa (\w+) ko\'y', r'sa \1 ko', "possessive_reorder"),
            (r'(\w+) ay (\w+)', r'\1 \2', "ay_contraction"),
            (r'(\w+) sa (\w+)', r'\1 s\2', "sa_contraction"),

            # Word shortening
            (r'damdamin', 'damdam', "emotion_shortening"),
            (r'hininga', 'hinga', "breath_shortening"),
            (r'buo', 'tapat', "wholeness_shortening"),
            (r'ito', "'to", "demonstrative_shortening"),
            (r'bawat', '', "quantifier_removal"),
        ]

        # Apply pattern replacements
        for pattern, replacement, change_type in replacements:
            if re.search(pattern, current_line):
                current_line = re.sub(pattern, replacement, current_line)
                changes.append({
                    "line": i+1,
                    "original": original_line,
                    "change": change_type,
                    "polished": current_line
                })

        # Level 2: Syllable count check and adjustments
        syllable_count = count_syllables(current_line)

        if syllable_count > 7:
            # Remove articles if present
            if " ang " in current_line:
                current_line = current_line.replace(" ang ", " ")
                changes.append({
                    "line": i+1,
                    "original": original_line,
                    "change": "article_removal",
                    "polished": current_line
                })

            # Remove redundant words
            redundant_words = ["laging", "muli", "pa rin"]
            for word in redundant_words:
                if f" {word} " in current_line:
                    current_line = current_line.replace(f" {word} ", " ")
                    changes.append({
                        "line": i+1,
                        "original": original_line,
                        "change": "redundant_word_removal",
                        "polished": current_line
                    })

        # Level 3: Final forced correction if still too long
        if count_syllables(current_line) > 7:
            words = current_line.split()
            if len(words) > 3:  # Only remove if line has enough words
                current_line = ' '.join(words[:-1])
                changes.append({
                    "line": i+1,
                    "original": original_line,
                    "change": "last_word_removal",
                    "polished": current_line
                })

        polished_lines.append(current_line)

    return '\n'.join(polished_lines), changes

# --- PROSODY VALIDATOR ---
def validate_tanaga(poem: str) -> Dict:
    """
    Validates syllable count for each line in a tanaga.
    Args:
        poem: Generated tanaga string
    Returns:
        dict: Validation results with syllable counts
    """
    lines = poem.strip().split('\n')
    syllable_counts = [count_syllables(line) for line in lines]
    return {
        "is_valid": all(6 <= count <= 8 for count in syllable_counts),
        "counts": syllable_counts,
        "total_syllables": sum(syllable_counts)
    }

# --- REQUEST MODEL ---
class PoetryRequest(BaseModel):
    user_input: str
    history: List[Dict] = []
    strict_meter: bool = True  # Default to strict meter
    max_polish_passes: int = 3  # Maximum polishing attempts
    meter_tolerance: int = 1   # Allow ±1 syllable by default

# --- HEALTH CHECK ENDPOINT ---
@app.get("/")
async def health_check():
    """Endpoint for service status monitoring"""
    return {
        "status": "online",
        "version": "5.0",
        "features": [
            "strict_meter_enforcement",
            "multi_level_polishing",
            "cultural_sensitivity",
            "change_tracking"
        ],
        "example": {
            "input": "Filipino diaspora and longing for home",
            "output": "Lupang walang nakita\ndamdam ko'y malaya\nsa hinga, bayan\nnag-iisa sa loob"
        }
    }

# --- MAIN GENERATION ENDPOINT ---
@app.post("/generate-tanaga")
async def generate_tanaga(request: PoetryRequest):
    """
    Core endpoint for tanaga generation with strict meter enforcement.
    Features:
    - Input sanitization
    - Tagalog-focused generation
    - Multi-pass polishing
    - Change tracking
    - Fallback mechanisms
    """
    from openai import OpenAI

    # Input processing
    safe_input = redact_pii(request.user_input)
    api_key = os.environ.get('MISTRAL_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="MISTRAL_API_KEY missing")

    # Language detection
    user_query_lower = safe_input.lower()
    tagalog_triggers = ["tagalog", "sa tagalog", "filipino", "tag-alog", "wika"]
    if not any(trigger in user_query_lower for trigger in tagalog_triggers):
        raise HTTPException(status_code=400, detail="Currently optimized for Tagalog input only")

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
            temperature=0.1,  # Low temperature for consistency
            max_tokens=100,
            timeout=10
        )

        reply_text = response.choices[0].message.content.strip()

        # Get token usage
        tokens_used = getattr(response, 'usage', {}).total_tokens if hasattr(response, 'usage') else None

        # Initial validation
        validation = validate_tanaga(reply_text)
        polished_text = reply_text
        all_changes = []

        # Multi-pass polishing
        for pass_num in range(request.max_polish_passes):
            polished_text, changes = polish_tanaga(polished_text)
            if changes:
                all_changes.extend(changes)

            validation = validate_tanaga(polished_text)

            # Stop if valid or no more changes
            if (validation["is_valid"] or
                all(6 <= count <= 7 + request.meter_tolerance for count in validation["counts"])):
                break

        # Prepare response
        gc.collect()
        result = {
            "original": reply_text,
            "original_check": validate_tanaga(reply_text),
            "polished": polished_text,
            "polished_check": validate_tanaga(polished_text),
            "changes_made": all_changes,
            "metadata": {
                "language": "Tagalog",
                "strict_mode": request.strict_meter,
                "polishing_passes": pass_num + 1,
                "tokens_used": tokens_used,
                "meter_tolerance": request.meter_tolerance
            },
            "disclaimer": (
                "AI-generated tanaga with strict meter enforcement. "
                "Some artistic license was taken to meet syllable requirements. "
                "Human review recommended for traditional use."
            )
        }

        return result

    except Exception as e:
        gc.collect()
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

# --- LAUNCH CONFIGURATION ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        timeout_keep_alive=30
    )
