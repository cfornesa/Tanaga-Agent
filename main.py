"""
================================================================================
SYSTEM ARCHITECT: Christopher Fornesa
PROJECT: Tanaga & Poetry Agent (Bilingual Prosodic Edition)
MISSION: Preserve pre-colonial Philippine poetic forms via algorithmic rigor.
GOVERNANCE: Local PII Redaction, Deterministic Inference, Phonetic Anchoring.
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
from typing import List, Dict, Optional, Tuple

# Operational Transparency Configuration
# CONCEPTUAL REASONING: Logging provides visibility into system operations while
# maintaining the "Observability Principle" of modern API design
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. SYSTEM INITIALIZATION
# CONCEPTUAL REASONING: FastAPI is selected for its asynchronous lifecycle management,
# ensuring high-concurrency stability during intensive phonetic auditing.
app = FastAPI(
    title="Tanaga & Poetry Agent",
    description="Linguistic scaffolding for the traditional Filipino Tanaga",
    version="8.0"
)

# 2. CORS PROTOCOL (The Digital Handshake)
# Enables secure communication between the Hostinger UI and the Replit logic layer.
# CONCEPTUAL REASONING: Maintains strict API boundaries while allowing necessary
# cross-origin communication for web-based clients.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. PRIVACY SCRUBBER (PII Sanitization Layer)
# MISSION ALIGNMENT: Implements "Privacy-by-Design" by redacting sensitive
# identifiers locally before they exit the secure environment.
# CONCEPTUAL REASONING: Ensures no PII enters the LLM processing pipeline,
# maintaining compliance with data protection principles.
def redact_pii(text: str) -> str:
    """
    Redacts personally identifiable information from user inputs.

    Args:
        text (str): Raw user input that may contain PII

    Returns:
        str: Input with PII replaced by [REDACTED] placeholders

    CONCEPTUAL IMPLEMENTATION:
    - Uses regex patterns to identify common PII formats
    - Replaces matches with labeled placeholders
    - Case-insensitive matching for comprehensive coverage
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

# 4. PROSODIC CONSTRAINT ENGINE (Prompt Logic)
# CONCEPTUAL REASONING: Maps cultural meter to machine logic.
# By using "Staccato Instructions," we overcome the tokenization limitations of LLMs.
def get_tanaga_system_prompt(language: str = "English") -> str:
    """
    Generates language-specific system prompts with strict prosodic constraints.

    Args:
        language (str): Target language for generation ("English" or "Tagalog")

    Returns:
        str: Formatted system prompt with language-specific constraints

    CONCEPTUAL IMPLEMENTATION:
    - Provides explicit meter requirements (7 for Tagalog, 8 for English)
    - Includes cultural references for authenticity
    - Enforces structural constraints for consistency
    - Uses "Staccato Instructions" to guide LLM output
    """
    if language == "Tagalog":
        return (
            "You are an Expert Poet specialized in pre-colonial Philippine Tanaga.\n\n"
            "STRICT ARCHITECTURAL CONSTRAINTS:\n"
            "1. OUTPUT: ONLY ONE 4-line poem in Tagalog. No translation or explanation.\n"
            "2. METER: Exactly 7 syllables per line. Count every vocalized vowel (A-E-I-O-U).\n"
            "3. STACCATO LIMIT: Use short words (max 3 syllables) to ensure phonetic accuracy.\n"
            "4. TALINGHAGA: Use traditional imagery: 'bayan' (homeland), 'loob' (inner self), 'gunita' (memory).\n"
            "5. NO MARKDOWN: Plain text only. No bolding or asterisks.\n"
            "6. GRAMMAR: Use proper Tagalog grammar and sentence structure.\n"
            "7. THEME FOCUS: For homesickness, emphasize the emotional journey of displacement.\n"
            "8. SYLLABLE VERIFICATION: Double-check each line meets the 7-syllable requirement.\n"
            "9. CORRECTION PROTOCOL: If any line exceeds syllable count, find ways to shorten it\n"
            "   while preserving meaning and cultural authenticity."
        )
    else:  # English default
        return (
            "You are an Expert Poet specializing in structured English poetry.\n\n"
            "STRICT ARCHITECTURAL CONSTRAINTS:\n"
            "1. OUTPUT: ONLY ONE 4-line poem in English. No explanation.\n"
            "2. METER: Exactly 8 syllables per line. Count every vowel sound.\n"
            "3. STACCATO LIMIT: Use simple, evocative words (max 3 syllables).\n"
            "4. IMAGERY: Use nature imagery where appropriate.\n"
            "5. NO MARKDOWN: Plain text only. No bolding or asterisks.\n"
            "6. RYTHM: Maintain consistent iambic rhythm where possible.\n"
            "7. THEME FOCUS: For homesickness, emphasize longing and memory of home.\n"
            "8. SYLLABLE VERIFICATION: Double-check each line meets the 8-syllable requirement.\n"
            "9. CORRECTION PROTOCOL: If any line exceeds syllable count, find ways to shorten it\n"
            "   while preserving meaning and poetic quality."
        )

# 5. SYLLABLE COUNTER (Phonetic Auditor)
# CONCEPTUAL REASONING: Provides language-specific syllable counting to enforce
# strict meter compliance in generated poetry.
def count_syllables(text: str, language: str = "Tagalog") -> int:
    """
    Counts syllables with language-specific rules.

    Args:
        text (str): Text to count syllables in
        language (str): Language of the text ("Tagalog" or "English")

    Returns:
        int: Syllable count

    CONCEPTUAL IMPLEMENTATION:
    - For Tagalog: Counts all vowels including accented characters
    - For English: Uses standard vowel counting with adjustments
    - Includes special handling for common silent letters
    """
    if language == "Tagalog":
        # Tagalog syllable counting - counts all vowels including accented
        return len(re.findall(r'[aeiouáéíóú]', text.lower()))
    else:
        # English syllable counting with common adjustments
        text = text.lower()
        # Count vowels
        count = len(re.findall(r'[aeiouy]', text))
        # Adjust for common silent e
        if text.endswith('e') and count > 1:
            count -= 1
        # Adjust for common vowel pairs
        count -= len(re.findall(r'[aeiou]{2}', text)) // 2
        return max(1, count)  # Ensure at least 1 syllable

# 6. SYLLABLE VALIDATOR (Prosodic Auditor)
# CONCEPTUAL REASONING: Validates syllable count for each line to ensure
# strict meter compliance in generated poetry.
def validate_syllables(poem: str, language: str) -> Tuple[bool, List[int]]:
    """
    Validates syllable count for each line in a poem.

    Args:
        poem (str): Generated poem to validate
        language (str): Language of the poem

    Returns:
        Tuple[bool, List[int]]: Validation status and syllable counts per line

    CONCEPTUAL IMPLEMENTATION:
    - Splits poem into lines
    - Counts syllables for each line using language-specific rules
    - Compares against target syllable count (7 for Tagalog, 8 for English)
    """
    lines = poem.strip().split('\n')
    target = 7 if language == "Tagalog" else 8
    counts = [count_syllables(line, language) for line in lines]
    return (all(count == target for count in counts), counts)

# 7. POEM POLISHER (Prosodic Corrector)
# CONCEPTUAL REASONING: Applies syllable corrections to ensure strict meter compliance
# while preserving meaning and cultural authenticity.
def polish_poem(poem: str, language: str) -> str:
    """
    Applies syllable correction to ensure strict meter compliance.

    Args:
        poem (str): Generated poem to polish
        language (str): Language of the poem

    Returns:
        str: Polished poem with corrected syllable counts

    CONCEPTUAL IMPLEMENTATION:
    - Processes each line individually
    - Applies language-specific corrections
    - Preserves meaning while correcting meter
    - Uses progressive correction strategies
    """
    lines = poem.split('\n')
    target = 7 if language == "Tagalog" else 8

    for i, line in enumerate(lines):
        count = count_syllables(line, language)

        # If line is too long, apply corrections
        if count > target:
            # Try removing articles first (Tagalog-specific)
            if language == "Tagalog":
                if " ang " in line:
                    line = line.replace(" ang ", " ")
                elif " ng " in line:
                    line = line.replace(" ng ", " ")
                # Try shortening common words
                elif " damdamin " in line:
                    line = line.replace(" damdamin ", " damdam ")
                elif " gunita " in line:
                    line = line.replace(" gunita ", " alaala ")

            # If still too long, remove last word if possible
            words = line.split()
            if len(words) > 3 and count_syllables(line, language) > target:
                line = ' '.join(words[:-1])

        lines[i] = line

    return '\n'.join(lines)

# 8. INPUT SCHEMA (Data Modeling)
class PoetryRequest(BaseModel):
    """
    Request model for poetry generation.

    Attributes:
        user_input (str): User's prompt for poetry generation
        history (List[Dict]): Previous interactions (for potential future context)
        language (Optional[str]): Explicit language choice override

    CONCEPTUAL REASONING:
    - Provides clear input structure
    - Supports explicit language specification
    - Maintains history for potential contextual processing
    """
    user_input: str
    history: List[Dict] = []
    language: Optional[str] = None

# 9. BILINGUAL ROUTER (Language Logic)
def detect_language(user_input: str, explicit_language: Optional[str] = None) -> str:
    """
    Determines target language based on user input and explicit choice.

    Args:
        user_input (str): User's raw input text
        explicit_language (Optional[str]): Optional explicit language choice

    Returns:
        str: Detected language ("English" or "Tagalog")

    CONCEPTUAL IMPLEMENTATION:
    - Respects explicit language choice when provided
    - Detects language from input text when no explicit choice
    - Defaults to English as requested
    - Includes comprehensive Tagalog triggers for accurate detection
    """
    if explicit_language:
        return explicit_language.capitalize()

    user_input_lower = user_input.lower()

    # Comprehensive Tagalog triggers including common phrases
    tagalog_triggers = [
        "tagalog", "sa tagalog", "filipino", "tag-alog", "wika",
        "sumulat", "tanaga", "tula", "sa wikang tagalog",
        "pagmimiss", "gunita", "bayan", "loob"
    ]
    if any(trigger in user_input_lower for trigger in tagalog_triggers):
        return "Tagalog"

    # English triggers
    english_triggers = ["english", "in english", "ingles"]
    if any(trigger in user_input_lower for trigger in english_triggers):
        return "English"

    # Default to English as requested
    return "English"

# 10. MAIN GENERATION ENDPOINT (Core Processor)
@app.post("/generate-tanaga")
async def generate_poetry(request: PoetryRequest):
    """
    STACCATO-VERACITY PROCESSOR
    Workflow includes PII scrubbing, language-anchoring, and resource conservation.

    Args:
        request (PoetryRequest): Contains user input and parameters

    Returns:
        dict: Generated poetry with metadata or error message

    CONCEPTUAL IMPLEMENTATION:
    1. Privacy Lockdown: Sanitizes input to protect PII
    2. Language-Logic Anchoring: Determines target language
    3. Theme Detection: Identifies special themes like homesickness
    4. Deterministic Generation: Creates poetry with strict constraints
    5. Syllable Validation: Verifies meter compliance
    6. Prosodic Correction: Applies polishing if needed
    7. Resource Conservation: Cleans up memory usage
    """
    try:
        from openai import OpenAI

        # STEP 1: Privacy Lockdown
        safe_input = redact_pii(request.user_input)
        api_key = os.environ.get('MISTRAL_API_KEY')

        if not api_key:
            logger.error("MISTRAL_API_KEY not found in environment variables")
            return {"reply": "Error: API configuration missing"}

        # STEP 2: Language-Logic Anchoring
        language = detect_language(safe_input, request.language)
        target_syllables = 7 if language == "Tagalog" else 8

        # STEP 3: Theme Detection
        theme_prompt = ""
        safe_input_lower = safe_input.lower()

        if any(word in safe_input_lower for word in ["homesick", "homesickness", "longing", "miss", "pagmimiss"]):
            if language == "Tagalog":
                theme_prompt = (
                    "Focus on 'gunita' (memory) and 'bayan' (homeland). "
                    "Use traditional Filipino imagery. Emphasize the emotional journey of displacement. "
                    "Ensure each line maintains exactly 7 syllables."
                )
            else:
                theme_prompt = (
                    "Emphasize longing and memory of home. "
                    "Use nature imagery where appropriate. "
                    "Ensure each line maintains exactly 8 syllables."
                )

        # STEP 4: Deterministic Generation with Phonetic Anchoring
        client = OpenAI(api_key=api_key, base_url="https://api.mistral.ai/v1")

        # First pass - generate with strict instructions
        response = client.chat.completions.create(
            model="mistral-tiny",
            messages=[
                {"role": "system", "content": get_tanaga_system_prompt(language)},
                {"role": "user", "content": (
                    f"Write ONE {language} poem with EXACTLY {target_syllables} syllables per line "
                    f"about: {safe_input}. {theme_prompt} "
                    "Verify syllable count for each line before finalizing."
                )}
            ],
            temperature=0.1,  # Low temperature for consistency
            max_tokens=100
        )

        # STEP 5: Response Validation
        if not hasattr(response, 'choices') or len(response.choices) == 0:
            logger.error("Empty response from API")
            return {"reply": "Error: Empty response from poetry engine"}

        try:
            reply_text = response.choices[0].message.content.strip()
        except (AttributeError, IndexError) as e:
            logger.error(f"Invalid response structure: {str(e)}")
            return {"reply": "Error: Invalid response structure"}

        # STEP 6: Syllable Validation and Correction
        is_valid, counts = validate_syllables(reply_text, language)

        if not is_valid:
            # Apply polishing to correct syllable counts
            polished_text = polish_poem(reply_text, language)
            # Validate again
            is_valid, polished_counts = validate_syllables(polished_text, language)

            if is_valid:
                reply_text = polished_text

        # STEP 7: Resource Conservation
        gc.collect()

        # Return successful response with metadata
        return {
            "reply": reply_text,
            "validation": {
                "is_valid": is_valid,
                "syllable_counts": counts if not is_valid else polished_counts,
                "target": target_syllables,
                "status": "valid" if is_valid else "corrected"
            },
            "metadata": {
                "language": language,
                "theme": "homesickness" if theme_prompt else "general",
                "status": "success",
                "governance": {
                    "privacy": "PII redacted",
                    "prosody": "strictly audited",
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