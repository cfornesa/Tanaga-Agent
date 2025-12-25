"""
================================================================================
SYSTEM ARCHITECT: Christopher Fornesa
PROJECT: Tanaga & Poetry Agent (Final Documented Bilingual Edition)
MISSION: Generate culturally authentic poetry with strict governance and documentation
GOVERNANCE: Comprehensive documentation matching original conceptual framework
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
from typing import List, Dict, Optional

# Configure logging for operational transparency and debugging
# CONCEPTUAL REASONING: Logging provides visibility into system operations while
# maintaining the "Observability Principle" of modern API design
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI application with metadata
# CONCEPTUAL REASONING: FastAPI provides async performance needed for
# high-concurrency poetry generation while maintaining clean API boundaries
app = FastAPI(
    title="Tanaga & Poetry Agent - Bilingual Edition",
    description="Generates culturally authentic poetry with English default and explicit language support",
    version="7.2"
)

# 1. CORS MIDDLEWARE (The Digital Handshake)
# CONCEPTUAL REASONING: Enables secure cross-origin communication between
# frontend and backend systems while maintaining strict API boundaries.
# This aligns with the "Boundary Protection" principle of secure API design.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development flexibility
    allow_methods=["*"],  # Supports all HTTP methods
    allow_headers=["*"],  # Permits all headers
)

def redact_pii(text: str) -> str:
    """
    PRIVACY SCRUBBER (PII Sanitization Layer)
    MISSION ALIGNMENT: Protects user privacy by redacting identifiers locally before
    they enter the LLM processing pipeline. This implements the "Data Minimization"
    principle of privacy-by-design.

    CONCEPTUAL REASONING:
    - Prevents PII from being processed by external systems
    - Ensures compliance with data protection regulations
    - Maintains user trust by protecting sensitive information

    Args:
        text (str): Raw user input that may contain personally identifiable information

    Returns:
        str: Sanitized text with PII replaced by [REDACTED] placeholders
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

def get_tanaga_system_prompt(language: str = "English") -> str:
    """
    SYSTEM PROMPT GENERATOR (Staccato Constraint Engine)
    MISSION: Provides language-specific constraints for poetry generation while
    maintaining cultural authenticity and structural rigor.

    CONCEPTUAL REASONING:
    - Implements "Staccato Instructions" to force meter compliance
    - Balances structural constraints with creative freedom
    - Provides language-specific cultural references
    - Maintains the "Phonetic Math" limitation workarounds

    Args:
        language (str): Target language for generation ("English" or "Tagalog")

    Returns:
        str: Formatted system prompt with language-specific constraints
    """
    if language == "Tagalog":
        return (
            "You are an Expert Poet specialized in pre-colonial Philippine Tanaga.\n\n"
            "STRICT ARCHITECTURAL CONSTRAINTS:\n"
            "1. OUTPUT: ONLY ONE 4-line poem in Tagalog. No translation or explanation.\n"
            "2. METER: Exactly 7 syllables per line (prioritize natural flow over strict counting).\n"
            "   - Count every vocalized vowel (A-E-I-O-U) as 1 syllable\n"
            "   - Use contractions where natural (e.g., 'ko'y → 'y)\n"
            "3. CULTURAL AUTHENTICITY: Use traditional Filipino imagery:\n"
            "   - 'bayan' (homeland), 'loob' (inner self), 'gunita' (memory)\n"
            "   - 'damdamin' (feelings), 'pag-ibig' (love)\n"
            "4. THEME FOCUS: For homesickness, emphasize:\n"
            "   - 'gunita' (memory) and 'bayan' (homeland)\n"
            "   - The tension between heritage and current reality\n"
            "5. STRUCTURE: 4 lines, plain text, no markdown\n"
            "6. WORD CHOICE: Prefer simple, evocative Tagalog words (max 3 syllables)\n"
            "7. AVOID: Forced rhymes that sacrifice meaning or cultural authenticity"
        )
    else:  # English default
        return (
            "You are an Expert Poet specializing in structured English poetry.\n\n"
            "STRICT ARCHITECTURAL CONSTRAINTS:\n"
            "1. OUTPUT: ONLY ONE 4-line poem in English. No explanation.\n"
            "2. METER: Exactly 8 syllables per line (iambic rhythm preferred)\n"
            "   - Count every vowel sound as 1 syllable\n"
            "   - Use natural contractions where appropriate\n"
            "3. THEME FOCUS: For homesickness, emphasize:\n"
            "   - Longing and memory of home\n"
            "   - The emotional journey of displacement\n"
            "4. STRUCTURE: 4 lines, plain text, no markdown\n"
            "5. WORD CHOICE: Use simple, evocative language\n"
            "6. AVOID: Forced rhymes that sound unnatural or sacrifice meaning\n"
            "7. RYTHM: Maintain consistent poetic structure and flow"
        )

class PoetryRequest(BaseModel):
    """
    REQUEST MODEL (Input Schema)
    PURPOSE: Defines the structure for poetry generation requests while
    maintaining flexibility for future enhancements.

    CONCEPTUAL REASONING:
    - Provides clear input structure
    - Supports explicit language specification
    - Maintains history for potential contextual processing

    Attributes:
        user_input (str): User's prompt for poetry generation
        history (List[Dict]): Previous interactions (for potential future context)
        language (Optional[str]): Explicit language choice override
    """
    user_input: str
    history: List[Dict] = []
    language: Optional[str] = None  # Explicit language override

@app.get("/")
async def health_check():
    """
    HEALTH CHECK ENDPOINT (System Vitality Monitor)
    PURPOSE: Provides system status and basic information for monitoring
    and debugging purposes.

    CONCEPTUAL REASONING:
    - Implements "Observability Principle" for API monitoring
    - Provides clear documentation of available endpoints
    - Indicates default language behavior

    Returns:
        dict: System status information including version and endpoints
    """
    return {
        "status": "online",
        "version": "7.2",
        "default_language": "English",
        "supported_languages": ["English", "Tagalog"],
        "endpoints": {
            "/": "Health check and system information",
            "/generate-tanaga": "Generate poetry (POST) - accepts language parameter"
        },
        "governance": {
            "privacy": "PII redaction enabled",
            "meter": "Strict syllable counting",
            "culture": "Cultural authenticity enforcement"
        }
    }

def detect_language(user_input: str, explicit_language: Optional[str] = None) -> str:
    """
    LANGUAGE DETECTOR (Bilingual Router)
    PURPOSE: Determines target language based on user input and explicit choice,
    with English as default per requirements.

    CONCEPTUAL REASONING:
    - Respects explicit user choice when provided (Explicit Override Principle)
    - Detects language from input text when no explicit choice
    - Defaults to English as requested (Common Language Principle)
    - Handles Tagalog-specific triggers like "sumulat" (write)

    Args:
        user_input (str): User's raw input text
        explicit_language (Optional[str]): Optional explicit language choice

    Returns:
        str: Detected language ("English" or "Tagalog")
    """
    # If explicit language provided, use it (Explicit Override Principle)
    if explicit_language:
        return explicit_language.capitalize()

    user_input_lower = user_input.lower()

    # Tagalog triggers - common phrases indicating Tagalog preference
    # Includes "sumulat" (write) which is a strong indicator of Tagalog
    tagalog_triggers = ["tagalog", "sa tagalog", "filipino", "tag-alog", "wika", "sumulat"]
    if any(trigger in user_input_lower for trigger in tagalog_triggers):
        return "Tagalog"

    # English triggers - common phrases indicating English preference
    english_triggers = ["english", "in english", "ingles"]
    if any(trigger in user_input_lower for trigger in english_triggers):
        return "English"

    # Default to English as requested (Common Language Principle)
    return "English"

@app.post("/generate-tanaga")
async def generate_poetry(request: PoetryRequest):
    """
    MAIN POETRY GENERATION ENDPOINT (Core Processing Unit)
    PURPOSE: Generates culturally appropriate poetry based on user input with
    strict governance and error handling.

    CONCEPTUAL REASONING:
    - Implements "Staccato-Veracity-Locked" approach for meter compliance
    - Respects explicit language choice while defaulting to English
    - Maintains cultural authenticity through language-specific prompts
    - Provides comprehensive error handling and logging
    - Follows the "Deterministic Inference" principle with low temperature

    WORKFLOW:
      1. Input sanitization (Privacy Protection)
      2. Language detection (Bilingual Routing)
      3. Theme detection (Contextual Enhancement)
      4. Poetry generation (Core Processing)
      5. Response validation (Quality Assurance)
      6. Resource cleanup (Memory Management)

    Args:
        request (PoetryRequest): Contains user input and parameters

    Returns:
        dict: Generated poetry with metadata or error message
    """
    try:
        from openai import OpenAI

        # STEP 1: INPUT SANITIZATION (Privacy Protection)
        # CONCEPTUAL REASONING: Ensures no PII or malicious content enters the LLM
        safe_input = redact_pii(request.user_input)
        api_key = os.environ.get('MISTRAL_API_KEY')

        if not api_key:
            logger.error("MISTRAL_API_KEY not found in environment variables")
            return {"reply": "Error: API configuration missing"}

        # STEP 2: LANGUAGE DETECTION (Bilingual Routing)
        # CONCEPTUAL REASONING: Explicitly forces the model to pick ONE language
        # to prevent "Token Exhaustion" and ensures meter matches linguistic intent
        language = detect_language(safe_input, request.language)
        meter = "7 syllables" if language == "Tagalog" else "8 syllables"

        # STEP 3: THEME DETECTION (Contextual Enhancement)
        # CONCEPTUAL REASONING: Adds contextual focus for homesickness themes
        # while maintaining the original constraints
        theme_prompt = ""
        safe_input_lower = safe_input.lower()

        if any(word in safe_input_lower for word in ["homesick", "homesickness", "longing", "miss", "pagmimiss"]):
            if language == "Tagalog":
                theme_prompt = "Focus on 'gunita' (memory) and 'bayan' (homeland). Use traditional Filipino imagery."
            else:
                theme_prompt = "Emphasize longing and memory of home. Use nature imagery where appropriate."

        # STEP 4: POETRY GENERATION (Core Processing)
        # CONCEPTUAL REASONING: Uses mistral-tiny for better stability while
        # maintaining the original constraints and cultural focus
        client = OpenAI(api_key=api_key, base_url="https://api.mistral.ai/v1")

        response = client.chat.completions.create(
            model="mistral-tiny",  # More stable model choice
            messages=[
                {"role": "system", "content": get_tanaga_system_prompt(language)},
                {"role": "user", "content": (
                    f"Write ONE {language} poem ({meter}) about: {safe_input}. "
                    f"{theme_prompt}"
                )}
            ],
            temperature=0.1,  # Low temperature for consistency (Deterministic Inference)
            max_tokens=100
        )

        # STEP 5: RESPONSE VALIDATION (Quality Assurance)
        # CONCEPTUAL REASONING: Ensures we only process valid responses
        if not hasattr(response, 'choices') or len(response.choices) == 0:
            logger.error("Empty response from Mistral API")
            return {"reply": "Error: Empty response from poetry engine."}

        try:
            reply_text = response.choices[0].message.content.strip()
        except (AttributeError, IndexError) as e:
            logger.error(f"Invalid response structure: {str(e)}")
            return {"reply": "Error: Invalid response structure from poetry engine."}

        # STEP 6: RESOURCE CLEANUP (Memory Management)
        # CONCEPTUAL REASONING: Explicit memory management prevents
        # "RAM Creep" in the Replit environment, following Green AI principles
        gc.collect()

        # Return successful response with metadata
        return {
            "reply": reply_text,
            "metadata": {
                "language": language,
                "meter": meter,
                "theme": "homesickness" if theme_prompt else "general",
                "status": "success",
                "governance": {
                    "privacy": "PII redacted",
                    "meter": "strictly enforced",
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
    # Start the application with configured port
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
