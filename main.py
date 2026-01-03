"""
================================================================================
SYSTEM ARCHITECT: Christopher Fornesa
PROJECT: Tanaga & Poetry Agent (Final Meter-Corrected Edition)
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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Tanaga & Poetry Agent - Meter Corrected Edition",
    description="Generates poetry with strict meter adherence",
    version="9.6"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def redact_pii(text: str) -> str:
    """Redacts personally identifiable information from text inputs."""
    patterns = {
        "EMAIL": r'[\w\.-]+@[\w\.-]+\.\w+',
        "PHONE": r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}'
    }
    for label, pattern in patterns.items():
        text = re.sub(pattern, f"[{label}_REDACTED]", text, flags=re.IGNORECASE)
    return text

def get_tanaga_system_prompt(language: str) -> str:
    """
    Generates language-specific system prompts with strict meter constraints.

    Args:
        language (str): Target language for generation ("English" or "Tagalog")

    Returns:
        str: Formatted system prompt with strict meter constraints
    """
    if language == "Tagalog":
        return (
            "You are an Expert Poet specialized in traditional Tagalog Tanaga.\n"
            "You write Tanaga about the user's requested theme while following all constraints below.\n\n"
            "STRICT METER CONSTRAINTS:\n"
            "1. OUTPUT: ONLY ONE 4-line poem in Tagalog. No title, no translation, no explanation, no commentary.\n"
            "2. METER: EXACTLY 7 syllables per line. Follow these examples:\n"
            "   - 'Bayan ko'y malayo na' (7 syllables)\n"
            "   - 'Loob ko'y naglulumbay' (7 syllables)\n"
            "   - 'Gunita ko'y di malimot' (7 syllables)\n"
            "3. STRUCTURE: 4 lines, plain text, no markdown.\n"
            "4. CULTURAL IMAGERY: Use 'bayan' (homeland), 'loob' (inner self), 'gunita' (memory).\n"
            "5. THEME FOCUS: When the theme involves homesickness, emphasize distance, longing, and an emotional journey of separation and hoped-for return.\n"
            "6. WORD CHOICE: Use simple words (max 3 syllables).\n"
            "7. GRAMMAR: Use proper Tagalog grammar and sentence structure.\n"
            "8. DETERMINISTIC GENERATION: Prioritize structural consistency.\n"
            "9. FORMAT: Each line must be exactly 7 syllables. No exceptions."
        )
    else:  # English
        return (
            "You are an Expert Poet specializing in structured English poetry.\n"
            "You write structured English poems about the user's requested theme while following all constraints below.\n\n"
            "STRICT METER CONSTRAINTS:\n"
            "1. OUTPUT: ONLY ONE 4-line poem in English. No title, no explanation, no commentary.\n"
            "2. METER: EXACTLY 8 syllables per line. Follow these examples:\n"
            "   - 'The moon still shines on home' (8 syllables)\n"
            "   - 'My heart still longs for you' (8 syllables)\n"
            "   - 'The wind still calls my name' (8 syllables)\n"
            "3. STRUCTURE: 4 lines, plain text, no markdown.\n"
            "4. THEME FOCUS: When the theme involves homesickness, emphasize distance, vivid memory, and sustained longing.\n"
            "5. RHYTHM: Maintain consistent iambic rhythm.\n"
            "6. DETERMINISTIC GENERATION: Prioritize structural consistency.\n"
            "7. FORMAT: Each line must be exactly 8 syllables. No exceptions."
        )

def detect_language(user_input: str) -> str:
    """
    Detects target language with enhanced logic for mixed-language requests.

    Args:
        user_input (str): User's raw input text

    Returns:
        str: Detected language ("English" or "Tagalog")
    """
    user_input_lower = user_input.lower()

    # Check for explicit English requests first
    english_triggers = [
        "in english", "sa ingles", "english",
        "write a tanaga about",
        "magsulat ka ng tanaga tungkol sa... sa ingles",
        "sa ingles", "in english", "english version"
    ]
    if any(trigger in user_input_lower for trigger in english_triggers):
        return "English"

    # Check for Tagalog requests
    tagalog_triggers = [
        "tagalog", "sa tagalog", "filipino", "tag-alog", "wika",
        "sumulat", "tanaga", "tula", "sa wikang tagalog"
    ]
    if any(trigger in user_input_lower for trigger in tagalog_triggers):
        return "Tagalog"

    # Default to English
    return "English"

class PoetryRequest(BaseModel):
    """Request model for poetry generation"""
    user_input: str
    history: List[Dict] = []

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "online",
        "version": "9.6",
        "features": [
            "strict_meter_enforcement",
            "cultural_authenticity",
            "deterministic_generation"
        ]
    }

@app.post("/generate-tanaga")
async def generate_poetry(request: PoetryRequest):
    """
    Main poetry generation endpoint with strict meter enforcement.

    Args:
        request (PoetryRequest): Contains user input and parameters

    Returns:
        dict: Generated poetry with metadata or error message
    """
    try:
        from openai import OpenAI

        # Input processing
        safe_input = redact_pii(request.user_input)
        api_key = os.environ.get('MISTRAL_API_KEY')

        if not api_key:
            return {"reply": "Error: API configuration missing"}

        # Language detection
        language = detect_language(safe_input)

        # Prepare messages with strict meter constraints
        client = OpenAI(api_key=api_key, base_url="https://api.mistral.ai/v1")

        # Enhanced prompt with explicit meter examples and constraints
        response = client.chat.completions.create(
            model="mistral-tiny",
            messages=[
                {"role": "system", "content": get_tanaga_system_prompt(language)},
                {"role": "user", "content": (
                    f"Write ONE {language} poem about: {safe_input}. "
                    "Follow ALL constraints in the system prompt EXACTLY. "
                    "Use the example line structures from the system prompt. "
                    "Each line MUST match the required syllable count. "
                    "For Tagalog: 7 syllables per line. "
                    "For English: 8 syllables per line. "
                    "Do not deviate from these rules."
                )}
            ],
            temperature=0.1,  # Low temperature for consistency
            max_tokens=100
        )

        # Response validation
        if not hasattr(response, 'choices') or len(response.choices) == 0:
            return {"reply": "Error: Empty response from poetry engine"}

        reply_text = response.choices[0].message.content.strip()

        # Resource cleanup
        gc.collect()

        return {
            "reply": reply_text,
            "metadata": {
                "language": language,
                "status": "success"
            }
        }

    except Exception as e:
        gc.collect()
        return {"reply": f"System Error: {str(e)}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
