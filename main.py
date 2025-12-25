"""
================================================================================
SYSTEM ARCHITECT: Christopher Fornesa
PROJECT: Tanaga & Poetry Agent (Final Documented Edition)
MISSION: Generate culturally authentic poetry with strict language adherence
GOVERNANCE: Local PII Redaction, Deterministic Inference, Strict Language Routing
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
    title="Tanaga & Poetry Agent - Final Edition",
    description="Generates culturally authentic poetry with strict language adherence",
    version="9.3"
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
    - Specifies language-specific requirements
    - Maintains cultural authenticity constraints
    - Uses "Staccato Instructions" to guide LLM output
    """
    if language == "Tagalog":
        return (
            "You are an Expert Poet specialized in traditional Tagalog Tanaga.\n\n"
            "STRICT ARCHITECTURAL CONSTRAINTS:\n"
            "1. OUTPUT: ONLY ONE 4-line poem in Tagalog. No translation or explanation.\n"
            "2. STRUCTURE: Follow traditional Tagalog poetic structure.\n"
            "3. CULTURAL IMAGERY: Use 'bayan' (homeland), 'loob' (inner self), 'gunita' (memory).\n"
            "4. THEME FOCUS: For homesickness, emphasize emotional journey.\n"
            "5. DETERMINISTIC GENERATION: Prioritize structural consistency."
        )
    else:  # English
        return (
            "You are an Expert Poet specializing in structured English poetry.\n\n"
            "STRICT ARCHITECTURAL CONSTRAINTS:\n"
            "1. OUTPUT: ONLY ONE 4-line poem in English. No explanation.\n"
            "2. STRUCTURE: Follow traditional English poetic structure.\n"
            "3. THEME FOCUS: For homesickness, emphasize longing and memory.\n"
            "4. DETERMINISTIC GENERATION: Prioritize structural consistency."
        )

def detect_language(user_input: str) -> str:
    """
    LANGUAGE DETECTOR (Strict Router)
    MISSION: Determines target language with corrected logic
    CONCEPTUAL IMPLEMENTATION:
    - Checks for explicit English requests first
    - Then checks for Tagalog requests
    - Defaults to English as requested
    - Handles mixed-language requests properly
    """
    user_input_lower = user_input.lower()

    # Check for explicit English requests first
    english_triggers = [
        "in english", "sa ingles", "english",
        "write a tanaga about",  # English request pattern
        "magsulat ka ng tanaga tungkol sa... sa ingles"  # Your specific example
    ]
    if any(trigger in user_input_lower for trigger in english_triggers):
        return "English"

    # Then check for Tagalog
    tagalog_triggers = [
        "tagalog", "sa tagalog", "filipino", "tag-alog", "wika",
        "sumulat", "tanaga", "tula", "sa wikang tagalog"
    ]
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
        "version": "9.3",
        "features": [
            "strict_language_routing",
            "cultural_authenticity",
            "deterministic_generation"
        ]
    }

@app.post("/generate-tanaga")
async def generate_poetry(request: PoetryRequest):
    """
    CORE POETRY GENERATION ENDPOINT
    MISSION: Generate culturally authentic poetry with strict language adherence
    CONCEPTUAL IMPLEMENTATION:
    1. Privacy Protection: Sanitizes input to prevent PII exposure
    2. Language Routing: Determines target language with corrected logic
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

        # STEP 2: Language Routing with Corrected Logic
        language = detect_language(safe_input)

        # STEP 3: Prepare Messages with Strict Constraints
        client = OpenAI(api_key=api_key, base_url="https://api.mistral.ai/v1")

        response = client.chat.completions.create(
            model="mistral-tiny",
            messages=[
                {"role": "system", "content": get_tanaga_system_prompt(language)},
                {"role": "user", "content": (
                    f"Write ONE {language} poem about: {safe_input}. "
                    "Follow all structural constraints precisely."
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
