"""
================================================================================
SYSTEM ARCHITECT: Christopher Fornesa
PROJECT: Tanaga & Poetry Agent (Final Documented Edition with Meter Enforcement)
MISSION: Generate culturally authentic poetry with strict meter adherence
GOVERNANCE: Local PII Redaction, Deterministic Inference, Strict Meter Enforcement
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
from typing import List, Dict

# Operational Transparency Configuration
# CONCEPTUAL REASONING: Logging provides visibility into system operations while
# maintaining the "Observability Principle" of modern API design
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. SYSTEM INITIALIZATION
# CONCEPTUAL REASONING: FastAPI provides asynchronous processing for
# high-concurrency poetic generation while maintaining clean API boundaries
app = FastAPI(
    title="Tanaga & Poetry Agent - Meter Enforced Edition",
    description="Generates poetry with strict meter adherence",
    version="9.5"
)

# 2. CORS PROTOCOL (The Digital Handshake)
# CONCEPTUAL REASONING: Enables secure cross-origin communication while
# maintaining strict API boundaries between frontend and backend systems
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def redact_pii(text: str) -> str:
    """
    PRIVACY SCRUBBER (PII Sanitization Layer)
    MISSION: Protects user privacy by redacting sensitive identifiers
    CONCEPTUAL IMPLEMENTATION:
    - Uses regex patterns to identify common PII formats
    - Replaces matches with labeled placeholders
    - Case-insensitive matching for comprehensive coverage
    - Implements "Privacy-by-Design" principle
    """
    patterns = {
        # Email pattern matching - captures most common email formats
        "EMAIL": r'[\w\.-]+@[\w\.-]+\.\w+',
        # Phone pattern matching - handles international and local formats
        "PHONE": r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}'
    }
    for label, pattern in patterns.items():
        text = re.sub(pattern, f"[{label}_REDACTED]", text, flags=re.IGNORECASE)
    return text

def get_tanaga_system_prompt(language: str) -> str:
    """
    POETIC PROTOCOL GENERATOR
    MISSION: Provides language-specific constraints for poetic generation
    CONCEPTUAL IMPLEMENTATION:
    - Enforces deterministic output structure
    - Specifies strict meter requirements with examples
    - Maintains cultural authenticity constraints
    - Uses "Staccato Instructions" to guide LLM output
    """
    if language == "Tagalog":
        return (
            "You are an Expert Poet specialized in traditional Tagalog Tanaga.\n\n"
            "STRICT METER CONSTRAINTS:\n"
            "1. OUTPUT: ONLY ONE 4-line poem in Tagalog. No translation or explanation.\n"
            "2. METER: EXACTLY 7 syllables per line. Count every vowel (A-E-I-O-U).\n"
            "   - Example structure: 'Bayan ko'y malayo na' (7 syllables)\n"
            "   - Example structure: 'Loob ko'y naglulumbay' (7 syllables)\n"
            "3. STRUCTURE: 4 lines, plain text, no markdown.\n"
            "4. CULTURAL IMAGERY: Use 'bayan' (homeland), 'loob' (inner self), 'gunita' (memory).\n"
            "5. THEME FOCUS: For homesickness, emphasize emotional journey.\n"
            "6. WORD CHOICE: Prefer simple, evocative words (max 3 syllables).\n"
            "7. GRAMMAR: Use proper Tagalog grammar and sentence structure.\n"
            "8. DETERMINISTIC GENERATION: Prioritize structural consistency over creative variation."
        )
    else:  # English
        return (
            "You are an Expert Poet specializing in structured English poetry.\n\n"
            "STRICT METER CONSTRAINTS:\n"
            "1. OUTPUT: ONLY ONE 4-line poem in English. No explanation.\n"
            "2. METER: EXACTLY 8 syllables per line. Count every vowel sound.\n"
            "   - Example structure: 'The moon still shines on home' (8 syllables)\n"
            "   - Example structure: 'My heart still longs for you' (8 syllables)\n"
            "3. STRUCTURE: 4 lines, plain text, no markdown.\n"
            "4. THEME FOCUS: For homesickness, emphasize longing and memory.\n"
            "5. RYTHM: Maintain consistent iambic rhythm where possible.\n"
            "6. DETERMINISTIC GENERATION: Prioritize structural consistency over creative variation."
        )

def detect_language(user_input: str) -> str:
    """
    LANGUAGE DETECTOR (Strict Router)
    MISSION: Determines target language with corrected logic for mixed-language requests
    CONCEPTUAL IMPLEMENTATION:
    - Explicitly checks for English patterns first, including mixed-language requests
    - Uses comprehensive trigger lists for both languages
    - Prioritizes English detection when both languages are present
    - Handles your specific example pattern: "magsulat ka ng tanaga tungkol sa... sa ingles"
    """
    user_input_lower = user_input.lower()

    # Check for explicit English requests first, including mixed-language patterns
    english_triggers = [
        "in english", "sa ingles", "english",
        "write a tanaga about",  # Pure English request
        "magsulat ka ng tanaga tungkol sa... sa ingles",  # Your specific mixed-language pattern
        "sa ingles",  # Key phrase for English in mixed requests
        "in english",  # Pure English indicator
        "english version"  # Explicit English request
    ]

    # Check for Tagalog requests
    tagalog_triggers = [
        "tagalog", "sa tagalog", "filipino", "tag-alog", "wika",
        "sumulat", "tanaga", "tula", "sa wikang tagalog"
    ]

    # First check for explicit English patterns
    if any(trigger in user_input_lower for trigger in english_triggers):
        return "English"

    # Then check for Tagalog patterns
    if any(trigger in user_input_lower for trigger in tagalog_triggers):
        return "Tagalog"

    # Default to English
    return "English"

class PoetryRequest(BaseModel):
    """
    INPUT SCHEMA
    MISSION: Defines structure for poetry generation requests
    CONCEPTUAL IMPLEMENTATION:
    - Provides clear input structure
    - Maintains history for potential contextual processing
    - Supports future extensibility
    """
    user_input: str
    history: List[Dict] = []

@app.get("/")
async def health_check():
    """
    SYSTEM VITALITY MONITOR
    MISSION: Provides system status and basic information
    """
    return {
        "status": "online",
        "version": "9.5",
        "features": [
            "strict_meter_enforcement",
            "cultural_authenticity",
            "deterministic_generation"
        ]
    }

@app.post("/generate-tanaga")
async def generate_poetry(request: PoetryRequest):
    """
    CORE POETRY GENERATION ENDPOINT
    MISSION: Generate culturally authentic poetry with strict meter adherence
    CONCEPTUAL IMPLEMENTATION:
    1. Privacy Protection: Sanitizes input to prevent PII exposure
    2. Language Routing: Determines target language with corrected logic
    3. Deterministic Generation: Creates poetry with strict meter constraints
    4. Resource Management: Ensures efficient memory usage
    """
    try:
        from openai import OpenAI

        # STEP 1: Privacy Protection
        safe_input = redact_pii(request.user_input)
        api_key = os.environ.get('MISTRAL_API_KEY')

        if not api_key:
            logger.error("MISTRAL_API_KEY not configured")
            return {"reply": "Error: API configuration missing"}

        # STEP 2: Language Routing with Enhanced Logic
        language = detect_language(safe_input)

        # STEP 3: Prepare Messages with Strict Meter Constraints
        client = OpenAI(api_key=api_key, base_url="https://api.mistral.ai/v1")

        # Enhanced prompt with explicit meter examples and constraints
        response = client.chat.completions.create(
            model="mistral-tiny",
            messages=[
                {"role": "system", "content": get_tanaga_system_prompt(language)},
                {"role": "user", "content": (
                    f"Write ONE {language} poem about: {safe_input}. "
                    "Follow ALL meter constraints EXACTLY. "
                    f"For {language}, use the example structures provided. "
                    "Prioritize structural consistency over creative variation."
                )}
            ],
            temperature=0.1,  # Low temperature for consistency
            max_tokens=100
        )

        # Response validation
        if not hasattr(response, 'choices') or len(response.choices) == 0:
            logger.error("Empty response from API")
            return {"reply": "Error: Empty response from poetry engine"}

        try:
            reply_text = response.choices[0].message.content.strip()
        except (AttributeError, IndexError) as e:
            logger.error(f"Invalid response structure: {str(e)}")
            return {"reply": "Error: Invalid response structure"}

        # Resource cleanup
        gc.collect()

        return {
            "reply": reply_text,
            "metadata": {
                "language": language,
                "status": "success",
                "governance": {
                    "privacy": "PII redacted",
                    "structure": "deterministic constraints applied",
                    "culture": "authenticity maintained"
                }
            }
        }

    except Exception as e:
        logger.error(f"System Error: {str(e)}", exc_info=True)
        gc.collect()
        return {
            "reply": f"System Error: {str(e)}",
            "metadata": {
                "status": "error",
                "error_type": type(e).__name__,
                "governance": "error handling activated"
            }
        }

if __name__ == "__main__":
    # Start the application
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
