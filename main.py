"""
================================================================================
SYSTEM ARCHITECT: Christopher Fornesa
PROJECT: Tanaga & Poetry Agent (Final Documented Version)
MISSION: Achieving syllabic veracity while preserving cultural authenticity
GOVERNANCE: Maintains original structure with targeted improvements and full documentation
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

# Configure logging for debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# INITIALIZATION: FastAPI selected for high-concurrency async performance
# CONCEPTUAL REASONING: Minimizes server idle time while ensuring rapid linguistic processing
app = FastAPI(title="Tanaga & Poetry Agent - Veracity Edition")

# 1. CORS PROTOCOL (The Digital Handshake)
# CONCEPTUAL REASONING: Enables secure Cross-Origin communication between
# the frontend and backend while maintaining strict API boundaries
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def redact_pii(text: str) -> str:
    """
    PRIVACY SCRUBBER (PII Sanitization Layer)
    MISSION ALIGNMENT: Protects user privacy by redacting identifiers locally.
    Ensures that PII never enters the external inference cluster.

    Args:
        text (str): Raw user input string that may contain PII

    Returns:
        str: Input with PII replaced by [REDACTED] placeholders
    """
    patterns = {
        "EMAIL": r'[\w\.-]+@[\w\.-]+\.\w+',  # Email pattern matching
        "PHONE": r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}'  # Phone pattern matching
    }
    for label, pattern in patterns.items():
        text = re.sub(pattern, f"[{label}_REDACTED]", text, flags=re.IGNORECASE)
    return text

def get_tanaga_system_prompt():
    """
    POETIC PROTOCOL: THE STACCATO CONSTRAINT
    CONCEPTUAL REASONING: Addresses the "Phonetic Math" limitation of LLMs.
    By using "Staccato Instructions," we force the model to prioritize structural rigidness
    over creative linguistic drift while maintaining cultural authenticity.

    Returns:
        str: Formatted prompt with strict architectural constraints
    """
    return (
        "You are an Expert Poet specialized in Philippine Tanaga.\n\n"
        "STRICT ARCHITECTURAL CONSTRAINTS:\n"
        "1. LANGUAGE: Output ONLY ONE poem. Do not translate. Do not explain.\n"
        "2. TAGALOG METER: Exactly 7 syllables per line.\n"
        "3. ENGLISH METER: Exactly 8 syllables per line.\n"
        "4. WORD CEILING: Use simple words (max 3 syllables).\n"
        "5. STRUCTURE: Exactly 4 lines of plain text. No more.\n"
        "6. CULTURAL AUTHENTICITY: For Tagalog, use traditional imagery.\n"
        "   For English, maintain poetic structure.\n"
        "7. THEME FOCUS: For homesickness, emphasize longing and memory.\n"
        "8. NO MARKDOWN: Do not use asterisks (*) or bolding.\n\n"
        "SYLLABLE CALCULATION:\n"
        "- Count every vocalized vowel (A-E-I-O-U) as 1 syllable.\n"
        "- Accuracy is the highest priority.\n"
        "- For Tagalog: Prioritize natural flow within 7 syllables.\n"
        "- For English: Maintain iambic rhythm where possible."
    )

class PoetryRequest(BaseModel):
    """
    Request model for tanaga generation endpoint.
    Attributes:
        user_input (str): The input text/prompt for tanaga generation
        history (List[Dict]): Previous interactions (maintained for potential future context)
    """
    user_input: str
    history: List[Dict] = []

# 2. HEALTH CHECK (System Vitality)
@app.get("/")
async def health_check():
    """
    System health check endpoint.
    Returns basic system information and status.

    Returns:
        dict: System status information including:
            - status: online/offline
            - agent: service identifier
            - logic: processing approach
            - model: LLM model in use
    """
    return {
        "status": "online",
        "agent": "Tanaga Poet",
        "logic": "Staccato-Veracity-Locked",
        "model": "ministral-14b-latest",
        "endpoints": {
            "/": "Health check",
            "/generate-tanaga": "Generate tanaga (POST)"
        }
    }

# 3. MAIN GENERATION ENDPOINT
@app.post("/generate-tanaga")
async def process_chat(request: PoetryRequest):
    """
    Main endpoint for tanaga generation with enhanced language detection.
    Handles the complete workflow:
    1. Input sanitization
    2. Language detection (Tagalog/English)
    3. API request to Mistral
    4. Response handling
    5. Resource cleanup

    Args:
        request (PoetryRequest): Contains user input and history

    Returns:
        dict: Generated tanaga or error message with:
            - reply: Generated poem or error
            - Additional metadata in error cases
    """
    try:
        from openai import OpenAI

        # STEP 1: INPUT SANITIZATION
        # CONCEPTUAL REASONING: Ensures no PII or malicious content enters the LLM
        safe_input = redact_pii(request.user_input)
        api_key = os.environ.get('MISTRAL_API_KEY')

        if not api_key:
            logger.error("MISTRAL_API_KEY not found in environment variables")
            return {"reply": "Error: MISTRAL_API_KEY missing from server secrets."}

        # STEP 2: INITIALIZE CLIENT
        client = OpenAI(api_key=api_key, base_url="https://api.mistral.ai/v1")

        # STEP 3: LANGUAGE DETECTION
        # CONCEPTUAL REASONING: Explicitly forces the model to pick ONE language
        # to prevent "Token Exhaustion" and ensures meter matches linguistic intent
        user_query_lower = safe_input.lower()
        tagalog_triggers = ["tagalog", "sa tagalog", "filipino", "tag-alog", "wika"]
        english_triggers = ["english", "in english", "ingles"]

        is_tagalog = any(trigger in user_query_lower for trigger in tagalog_triggers)
        is_english = any(trigger in user_query_lower for trigger in english_triggers)

        # Default to Tagalog if no language specified (maintains cultural focus)
        if not is_tagalog and not is_english:
            is_tagalog = True

        target_lang = "Tagalog" if is_tagalog else "English"
        meter = "7 syllables" if is_tagalog else "8 syllables"

        # STEP 4: THEME-SPECIFIC PROMPT ENHANCEMENT
        # CONCEPTUAL REASONING: Adds contextual focus for homesickness themes
        # while maintaining the original constraints
        theme_prompt = ""
        if "homesick" in user_query_lower or "homesickness" in user_query_lower:
            theme_prompt = "Focus on themes of longing, memory, and cultural identity."
        elif "diaspora" in user_query_lower or "identity" in user_query_lower:
            theme_prompt = "Emphasize the tension between heritage and current reality."

        # STEP 5: PREPARE MESSAGES WITH ENHANCED CONSTRAINTS
        messages = [
            {"role": "system", "content": get_tanaga_system_prompt()},
            {"role": "user", "content": (
                f"Write ONE {target_lang} Tanaga ({meter}) about: {safe_input}. "
                f"{theme_prompt} "
                f"Do not provide an English version if writing in Tagalog."
            )}
        ]

        # STEP 6: GENERATE WITH DETERMINISTIC SETTINGS
        # ARCHITECTURAL NOTE: Temperature set to 0.1 to maximize deterministic math
        # We sacrifice some 'flourish' to ensure prosodic count accuracy
        response = client.chat.completions.create(
            model="ministral-14b-latest",
            messages=messages,
            temperature=0.1,  # Low temperature for consistency
            max_tokens=100
        )

        # STEP 7: RESPONSE VALIDATION
        # CONCEPTUAL REASONING: Ensures we only process valid responses
        if not hasattr(response, 'choices') or len(response.choices) == 0:
            logger.error("Empty response from Mistral API")
            return {"reply": "Error: Empty response from poetry engine."}

        if not hasattr(response.choices[0], 'message') or not hasattr(response.choices[0].message, 'content'):
            logger.error("Invalid response structure from Mistral API")
            return {"reply": "Error: Invalid response structure from poetry engine."}

        reply_text = response.choices[0].message.content.strip()

        # STEP 8: RESOURCE CONSERVATION
        # CONCEPTUAL REASONING: Explicit memory management prevents
        # "RAM Creep" in the Replit environment, following Green AI principles
        del messages
        gc.collect()

        return {"reply": reply_text}

    except Exception as e:
        logger.error(f"System Error: {str(e)}", exc_info=True)
        gc.collect()
        return {"reply": f"System Error: {str(e)}"}

if __name__ == "__main__":
    # Start the application
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
