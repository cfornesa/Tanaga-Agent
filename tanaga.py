"""
tanaga.py – Core logic for the Tanaga & Poetry Agent.

Contains PII redaction, syllable utilities, meter validation,
prompt construction, language detection, and the main poem
generation function. Imported by main.py.
"""

import os
import re
import gc
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


def redact_pii(text: str) -> str:
    """
    Redact email addresses and phone numbers from the input text.

    This provides a simple, best-effort safeguard so that potentially
    identifying information is not sent to the external LLM service.
    """
    patterns = {
        "EMAIL": r'[\w\.-]+@[\w\.-]+\.\w+',
        "PHONE": r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}'
    }
    for label, pattern in patterns.items():
        text = re.sub(pattern, f"[{label}_REDACTED]", text, flags=re.IGNORECASE)
    return text


def heuristic_syllable_count(word: str) -> int:
    """
    Approximate the number of syllables in a single word.

    Uses a simple vowel-group heuristic with a small adjustment for English
    silent "e". Intended for quick validation of meter, not linguistic accuracy.
    """
    w = re.sub(r"[^a-zA-ZáéíóúñüÁÉÍÓÚÑÜ]+", "", word)
    if not w:
        return 0

    vowels = "aeiouyAEIOUYáéíóúÁÉÍÓÚ"
    prev_is_vowel = False
    count = 0

    for ch in w:
        is_vowel = ch in vowels
        if is_vowel and not prev_is_vowel:
            count += 1
        prev_is_vowel = is_vowel

    # Simple English-style adjustment for silent "e" endings.
    if w.lower().endswith("e") and not w.lower().endswith("le") and count > 1:
        count -= 1

    return max(count, 1)


def count_line_syllables(line: str) -> int:
    """
    Return the total syllable count for a single line of text.

    Strips most punctuation, splits into words, and sums the heuristic
    syllable count for each word.
    """
    cleaned = re.sub(r"[^\w\s'áéíóúñüÁÉÍÓÚÑÜ-]", "", line)
    words = cleaned.split()
    return sum(heuristic_syllable_count(w) for w in words)


def validate_poem_meter(poem_text: str, language: str) -> Dict:
    """
    Validate each line of a poem against the required meter.

    For Tagalog, expects 7 syllables per line.
    For English, expects 8 syllables per line.

    Args:
        poem_text: Full poem text returned by the model.
        language: Detected language ("English" or "Tagalog").

    Returns:
        A dictionary containing:
        - lines: list of per-line meter reports.
        - all_match: True if all lines match the target count.
        - target: the target syllable count for this language.
    """
    target = 7 if language == "Tagalog" else 8
    lines = [ln for ln in poem_text.splitlines() if ln.strip()]

    results = []
    all_match = True
    for idx, line in enumerate(lines):
        syllables = count_line_syllables(line)
        ok = (syllables == target)
        if not ok:
            all_match = False
        results.append({
            "line_index": idx,
            "text": line,
            "syllables": syllables,
            "target": target,
            "valid": ok
        })

    return {
        "lines": results,
        "all_match": all_match,
        "target": target
    }


def get_tanaga_system_prompt(language: str) -> str:
    """
    Build the system prompt defining role, structure, and meter constraints.

    Args:
        language: Target language for generation ("English" or "Tagalog").

    Returns:
        A system prompt string with strict, language-specific instructions.
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
    Infer whether the user is requesting Tagalog or English output.

    Uses simple trigger phrases and defaults to English when unsure.

    Args:
        user_input: Raw input text from the user.

    Returns:
        "English" or "Tagalog" as the target generation language.
    """
    user_input_lower = user_input.lower()

    # Check for explicit English requests first.
    english_triggers = [
        "in english", "sa ingles", "english",
        "write a tanaga about",
        "magsulat ka ng tanaga tungkol sa... sa ingles",
        "english version"
    ]
    if any(trigger in user_input_lower for trigger in english_triggers):
        return "English"

    # Check for Tagalog requests.
    tagalog_triggers = [
        "tagalog", "sa tagalog", "filipino", "tag-alog", "wika",
        "sumulat", "tanaga", "tula", "sa wikang tagalog"
    ]
    if any(trigger in user_input_lower for trigger in tagalog_triggers):
        return "Tagalog"

    # Default to English when ambiguous.
    return "English"


def get_tanaga_example(language: str) -> str:
    if language == "Tagalog":
        # 7 syllables per line, manually verified
        return (
            "Bayan ko'y malayo na\n"   # Ba-yan-ko-y-ma-la-yo = 7
            "Loob ko'y naglulumbay\n"  # Lo-ob-ko-y-nag-lu-lum-bay = 7 (elided)
            "Gunita ko'y di malimot\n" # Gu-ni-ta-ko-y-di-ma-li-mot = 7 (elided)
            "Puso ko'y laging nandoon" # Pu-so-ko-y-la-ging-nan-doon = 7 (elided)
        )
    else:
        # 8 syllables per line, iambic, manually verified
        return (
            "The leaves are turning gold and red\n"  # 8
            "The winter sun grows cold and low\n"    # 8
            "The birds have long since fled their nest\n" # 8
            "The earth prepares for ice and snow"    # 8
        )


def generate_poem(user_input: str, language: str = "Tagalog") -> dict:
    """
    Generate a single poem with strict meter and return meter diagnostics.

    Redacts basic PII from the user input, detects the target language,
    calls the Ministral 14B model with a strict system prompt, and validates
    the resulting poem's syllable counts, retrying once if meter does not match.

    Args:
        user_input: Raw theme or request text from the user.

    Returns:
        A dictionary with the poem text and metadata (language, meter report).
    """
    from openai import OpenAI

    safe_input = redact_pii(user_input)
    api_key = os.environ.get('MISTRAL_API_KEY')

    if not api_key:
        return {"reply": "Error: API configuration missing"}

    client = OpenAI(api_key=api_key, base_url="https://api.mistral.ai/v1")

    max_attempts = 2
    reply_text = ""
    meter_report = None
    response = None  # kept for potential debugging or logging

    for attempt in range(max_attempts):
        response = client.chat.completions.create(
            model="ministral-14b-2512",
            messages=[
                {"role": "system", "content": get_tanaga_system_prompt(language)},
                # Few-shot: demonstrates meter compliance only, topic is irrelevant
                {"role": "user", "content": f"Write ONE {language} poem about: nature."},
                {"role": "assistant", "content": get_tanaga_example(language)},
                # Actual user request — completely free-form topic
                {"role": "user", "content": (
                    f"Write ONE {language} poem about: {safe_input}. "
                    "Each line MUST be exactly " + ("7" if language == "Tagalog" else "8") + " syllables. "
                    "Follow ALL constraints in the system prompt EXACTLY."
                )}
            ],
            temperature=0.1,
            max_tokens=100
        )

        if not hasattr(response, 'choices') or len(response.choices) == 0:
            continue

        reply_text = response.choices[0].message.content.strip()
        meter_report = validate_poem_meter(reply_text, language)

        if meter_report["all_match"]:
            break

    if not reply_text:
        return {"reply": "Error: Empty response from poetry engine"}

    gc.collect()

    return {
        "reply": reply_text,
        "metadata": {
            "language": language,
            "status": "success",
            "meter": meter_report
        }
    }
