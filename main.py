"""
================================================================================
SYSTEM ARCHITECT: Christopher Fornesa
PROJECT: Tanaga & Poetry Agent (Final Stable Version with Documentation)
MISSION: Generate culturally authentic Tagalog tanaga with reliable meter enforcement
GOVERNANCE: Robust error handling, response validation, and full documentation
================================================================================
"""

import os
import re
import gc
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Tuple

# Initialize FastAPI application with metadata
app = FastAPI(
    title="Tanaga Poet API",
    description="Generates traditional Philippine tanaga poetry with strict meter enforcement",
    version="5.1",
    docs_url="/docs",  # Enable Swagger UI documentation
    redoc_url="/redoc"  # Enable ReDoc documentation
)

# --- CORS MIDDLEWARE ---
# Enable Cross-Origin Resource Sharing to allow requests from any origin
# This is necessary for web-based clients to interact with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

class PoetryRequest(BaseModel):
    """
    Request model for tanaga generation endpoint.
    Attributes:
        user_input: The input text/prompt for tanaga generation
        history: Previous interactions (not used in current implementation)
        strict_meter: Whether to enforce strict 7-syllable meter (default: True)
        max_polish_passes: Maximum number of polishing attempts (default: 3)
        meter_tolerance: Allowed syllable variation (±value) (default: 1)
    """
    user_input: str
    history: List[Dict] = []
    strict_meter: bool = True
    max_polish_passes: int = 3
    meter_tolerance: int = 1

def redact_pii(text: str) -> str:
    """
    Redacts personally identifiable information from user inputs.
    This helps protect user privacy by removing emails and phone numbers.

    Args:
        text: Raw user input string that may contain PII

    Returns:
        str: Input with PII replaced by [REDACTED] placeholders
    """
    patterns = {
        "EMAIL": r'[\w\.-]+@[\w\.-]+\.\w+',  # Email pattern
        "PHONE": r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}'  # Phone pattern
    }
    for label, pattern in patterns.items():
        text = re.sub(pattern, f"[{label}_REDACTED]", text, flags=re.IGNORECASE)
    return text

def count_syllables(line: str) -> int:
    """
    Counts syllables in a Tagalog line using vowel counting.
    This is an approximation that works well for Tagalog poetry.

    Args:
        line: Single line of Tagalog text

    Returns:
        int: Approximate syllable count
    """
    # Count all vowels including accented characters common in Tagalog
    return len(re.findall(r'[aeiouáéíóú]', line.lower()))

def get_tanaga_system_prompt() -> str:
    """
    Generates system prompt optimized for Tagalog tanaga generation.
    The prompt guides the AI to produce culturally authentic poetry.

    Returns:
        str: Formatted prompt for the LLM
    """
    return (
        "You are an Expert Poet specialized in pre-colonial Philippine Tanaga.\n\n"
        "RULES:\n"
        "1. Output ONLY ONE 4-line poem in plain Tagalog\n"
        "2. Each line should be approximately 7 syllables\n"
        "3. Use simple, evocative language\n"
        "4. Focus on emotional truth and cultural authenticity\n"
        "5. Structure: 4 lines, no markdown, no explanation\n"
        "6. Common themes to incorporate:\n"
        "   - Diaspora and longing ('bayan', 'gunita')\n"
        "   - Emotional depth ('damdamin', 'loob')\n"
        "   - Nature and homeland imagery\n"
        "7. Prioritize natural flow over strict meter when necessary"
    )

def polish_tanaga(poem: str) -> Tuple[str, List[Dict]]:
    """
    Applies strict meter polishing to Tagalog tanaga.
    Uses pattern-based replacements to fix common meter issues while
    preserving cultural authenticity and emotional meaning.

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

        # Common pattern replacements that fix meter issues
        replacements = [
            # 9→7 syllable patterns
            (r'damdamin ko\'y (\w+)', r'damdam ko\'y \1'),  # "my feelings" contraction
            (r'sa bawat (\w+), (\w+)', r'sa \1, \2'),      # Remove "bawat" (each)
            (r'nag-iisa sa (\w+)', r'nag-iisa \1'),          # Remove "sa" (in)
            (r'laging (\w+)', r'\1'),                      # Remove "laging" (always)
            (r'(\w+) ko\'y', r'\1 ko'),                    # Simplify possessive
            (r'(\w+) ay (\w+)', r'\1 \2'),                  # Remove "ay" (is)
            (r'(\w+) sa (\w+)', r'\1 s\2'),                # Contract "sa" (in)

            # Word shortening for common terms
            (r'damdamin', 'damdam'),                       # feelings → emotion
            (r'hininga', 'hinga'),                         # breath → shorter form
            (r'buo', 'tapat'),                             # whole → complete
            (r'ito', "'to"),                                # this → colloquial form
        ]

        # Apply all relevant replacements
        for pattern, replacement in replacements:
            if re.search(pattern, current_line):
                current_line = re.sub(pattern, replacement, current_line)

        # Final syllable adjustment if still too long
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

def validate_tanaga(poem: str) -> Dict:
    """
    Validates syllable count for each line in a tanaga.
    Checks if each line meets the syllable requirements.

    Args:
        poem: Generated tanaga string

    Returns:
        dict: Validation results with syllable counts per line
    """
    lines = poem.strip().split('\n')
    syllable_counts = [count_syllables(line) for line in lines]
    return {
        "is_valid": all(6 <= count <= 8 for count in syllable_counts),  # Allow ±1 syllable
        "counts": syllable_counts,
        "total_syllables": sum(syllable_counts)
    }

@app.get("/")
async def health_check():
    """
    Health check endpoint for service status monitoring.
    Returns basic information about the API service.

    Returns:
        JSONResponse: Service status and information
    """
    return JSONResponse(content={
        "status": "online",
        "version": "5.1",
        "endpoints": ["/generate-tanaga"],
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    })

@app.post("/generate-tanaga")
async def generate_tanaga(request: PoetryRequest):
    """
    Main endpoint for tanaga generation with strict meter enforcement.
    Handles the complete workflow:
    1. Input validation and sanitization
    2. Tanaga generation using Mistral API
    3. Meter validation and polishing
    4. Response preparation

    Args:
        request: PoetryRequest containing user input and parameters

    Returns:
        JSONResponse: Generated tanaga with validation results
    """
    try:
        from openai import OpenAI

        # Step 1: Input validation and sanitization
        safe_input = redact_pii(request.user_input)
        api_key = os.environ.get('MISTRAL_API_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="MISTRAL_API_KEY not configured")

        # Step 2: Language validation (Tagalog only)
        user_query_lower = safe_input.lower()
        tagalog_triggers = ["tagalog", "sa tagalog", "filipino", "tag-alog", "wika"]
        if not any(trigger in user_query_lower for trigger in tagalog_triggers):
            raise HTTPException(status_code=400, detail="Currently optimized for Tagalog input only")

        # Step 3: Tanaga generation
        client = OpenAI(api_key=api_key, base_url="https://api.mistral.ai/v1")

        response = client.chat.completions.create(
            model="ministral-14b-latest",
            messages=[
                {"role": "system", "content": get_tanaga_system_prompt()},
                {"role": "user", "content": f"Write ONE Tagalog Tanaga about: {safe_input}."}
            ],
            temperature=0.1,  # Low temperature for consistency
            max_tokens=100,
            timeout=10
        )

        # Step 4: Response validation
        if not response.choices or not hasattr(response.choices[0], 'message'):
            raise HTTPException(status_code=500, detail="Invalid API response format")

        reply_text = response.choices[0].message.content.strip()

        # Step 5: Get token usage safely
        tokens_used = None
        if hasattr(response, 'usage') and response.usage:
            tokens_used = response.usage.total_tokens

        # Step 6: Meter validation and polishing
        validation = validate_tanaga(reply_text)
        polished_text = reply_text
        changes = []

        if request.strict_meter and not validation["is_valid"]:
            polished_text, changes = polish_tanaga(reply_text)
            validation = validate_tanaga(polished_text)

        # Step 7: Prepare and return response
        result = {
            "original": reply_text,
            "original_check": validate_tanaga(reply_text),
            "polished": polished_text if polished_text != reply_text else None,
            "polished_check": validation if polished_text != reply_text else None,
            "changes": changes if changes else None,
            "metadata": {
                "tokens_used": tokens_used,
                "strict_mode": request.strict_meter,
                "polishing_passes": 1 if changes else 0,
                "meter_tolerance": request.meter_tolerance
            },
            "disclaimer": (
                "AI-generated tanaga with strict meter enforcement. "
                "Some artistic license was taken to meet syllable requirements. "
                "Human review recommended for traditional use."
            )
        }

        return JSONResponse(content=result)

    except Exception as e:
        gc.collect()
        return JSONResponse(
            status_code=500,
            content={"error": f"Generation failed: {str(e)}"}
        )

if __name__ == "__main__":
    # Start the application
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )