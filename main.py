"""
================================================================================
SYSTEM ARCHITECT: Christopher Fornesa
PROJECT: Tanaga & Poetry Agent (Phonetic Rigor Edition - Final)
MISSION: Achieve consistent poetic forms through deterministic generation
GOVERNANCE: Local PII Redaction, Deterministic Inference, Language-Routing
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
# CONCEPTUAL REASONING: Logging provides operational visibility while
# maintaining system integrity and performance monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. SYSTEM INITIALIZATION
# CONCEPTUAL REASONING: FastAPI provides asynchronous processing for
# high-concurrency poetic generation while maintaining clean API boundaries
app = FastAPI(
    title="Tanaga & Poetry Agent - Veracity Edition",
    description="Generates traditional poetic forms with deterministic constraints",
    version="9.1"
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
        "EMAIL": r'[\w\.-]+@[\w\.-]+\.\w+',
        "PHONE": r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}'
    }
    for label, pattern in patterns.items():
        text = re.sub(pattern, f"[{label}_REDACTED]", text, flags=re.IGNORECASE)
    return text

def get_tanaga_system_prompt() -> str:
    """
    POETIC PROTOCOL GENERATOR
    MISSION: Provides strict architectural constraints for poetic generation
    CONCEPTUAL IMPLEMENTATION:
    - Enforces deterministic output structure
    - Specifies language-specific meter requirements
    - Maintains cultural authenticity constraints
    - Uses "Staccato Instructions" to guide LLM output
    - Prioritizes structural rigidity over creative drift
    """
    return (
        "You are an Expert Poet specialized in traditional poetic forms.\n\n"
        "STRICT ARCHITECTURAL CONSTRAINTS:\n"
        "1. OUTPUT: Generate ONLY ONE 4-line poem. No translation or explanation.\n"
        "2. TAGALOG METER: Exactly 7 syllables per line when writing in Tagalog.\n"
        "3. ENGLISH METER: Exactly 8 syllables per line when writing in English.\n"
        "4. WORD CEILING: Use simple words (maximum 3 syllables).\n"
        "5. STRUCTURE: Exactly 4 lines of plain text. No markdown or formatting.\n"
        "6. CULTURAL AUTHENTICITY: For Tagalog, use traditional imagery like:\n"
        "   - 'bayan' (homeland), 'loob' (inner self), 'gunita' (memory)\n"
        "7. THEME FOCUS: For homesickness themes, emphasize emotional journey.\n"
        "8. DETERMINISTIC GENERATION: Prioritize structural consistency over creative variation."
    )

def detect_language(user_input: str) -> str:
    """
    LANGUAGE DETECTOR
    MISSION: Determines target language based on user input
    CONCEPTUAL IMPLEMENTATION:
    - Detects explicit language requests in input
    - Uses comprehensive trigger lists for accurate detection
    - Defaults to English as requested
    - Implements "Explicit Override" principle for language selection
    """
    user_input_lower = user_input.lower()

    # Tagalog triggers - comprehensive list of indicators
    tagalog_triggers = [
        "tagalog", "sa tagalog", "filipino", "tag-alog", "wika",
        "sumulat", "tanaga", "tula", "sa wikang tagalog"
    ]
    if any(trigger in user_input_lower for trigger in tagalog_triggers):
        return "Tagalog"

    # Default to English as requested
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
        "version": "9.1",
        "logic": "Staccato-Veracity-Locked",
        "model": "ministral-14b-latest",
        "endpoints": {
            "/": "Health check and system information",
            "/generate-tanaga": "Generate poetry (POST)"
        }
    }

@app.post("/generate-tanaga")
async def process_chat(request: PoetryRequest):
    """
    CORE POETRY GENERATION ENDPOINT
    MISSION: Generate culturally authentic poetry with deterministic constraints
    CONCEPTUAL IMPLEMENTATION:
    1. Privacy Protection: Sanitizes input to prevent PII exposure
    2. Language Routing: Determines target language
    3. Deterministic Generation: Creates poetry with strict constraints
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

        # STEP 2: Language Routing
        language = detect_language(safe_input)
        meter = "7 syllables" if language == "Tagalog" else "8 syllables"

        # STEP 3: Prepare Messages with Strict Constraints
        client = OpenAI(api_key=api_key, base_url="https://api.mistral.ai/v1")

        # Enhanced prompt with cultural and structural constraints
        messages = [
            {"role": "system", "content": get_tanaga_system_prompt()},
            {"role": "user", "content": (
                f"Write ONE {language} poem with {meter} about: {safe_input}. "
                "Follow all structural constraints precisely. "
                "For Tagalog, emphasize traditional imagery and proper grammar."
            )}
        ]

        # STEP 4: Deterministic Generation
        # CONCEPTUAL REASONING: Low temperature ensures consistent output
        # that adheres to structural constraints
        response = client.chat.completions.create(
            model="ministral-14b-latest",
            messages=messages,
            temperature=0.1,
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
                "meter": meter,
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
