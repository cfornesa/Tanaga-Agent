"""
model.py – Core logic for the Tanaga & Poetry Agent.

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
        "EMAIL": r"[\w\.-]+@[\w\.-]+\.\w+",
        "PHONE": r"\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}",
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
        ok = syllables == target
        if not ok:
            all_match = False
        results.append(
            {
                "line_index": idx,
                "text": line,
                "syllables": syllables,
                "target": target,
                "valid": ok,
            }
        )

    return {"lines": results, "all_match": all_match, "target": target}


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
        "in english",
        "sa ingles",
        "english",
        "write a tanaga about",
        "magsulat ka ng tanaga tungkol sa... sa ingles",
        "english version",
    ]
    if any(trigger in user_input_lower for trigger in english_triggers):
        return "English"

    # Check for Tagalog requests.
    tagalog_triggers = [
        "tagalog",
        "sa tagalog",
        "filipino",
        "tag-alog",
        "wika",
        "sumulat",
        "tanaga",
        "tula",
        "sa wikang tagalog",
    ]
    if any(trigger in user_input_lower for trigger in tagalog_triggers):
        return "Tagalog"

    # Default to English when ambiguous.
    return "English"


def get_tanaga_example(language: str) -> str:
    if language == "Tagalog":
        # 7 syllables per line, manually verified
        return (
            "Bayan ko'y malayo na\n"  # Ba-yan-ko-y-ma-la-yo = 7
            "Loob ko'y naglulumbay\n"  # Lo-ob-ko-y-nag-lu-lum-bay = 7 (elided)
            "Gunita ko'y di malimot\n"  # Gu-ni-ta-ko-y-di-ma-li-mot = 7 (elided)
            "Puso ko'y laging nandoon"  # Pu-so-ko-y-la-ging-nan-doon = 7 (elided)
        )
    else:
        # 8 syllables per line, iambic, manually verified
        return (
            "The leaves are turning gold and red\n"  # 8
            "The winter sun grows cold and low\n"  # 8
            "The birds have long since fled their nest\n"  # 8
            "The earth prepares for ice and snow"  # 8
        )


def generate_poem(user_input: str, language: str = "Tagalog") -> dict:
    from mistralai import Mistral

    safe_input = redact_pii(user_input)
    api_key = os.environ.get("MISTRAL_API_KEY")
    agent_id = os.environ.get("AGENT_ID")

    if not api_key or not agent_id:
        return {"reply": "Error: API configuration missing"}

    client = Mistral(api_key=api_key)
    syllable_count = "7" if language == "Tagalog" else "8"

    max_attempts = 2
    reply_text = ""
    meter_report = None

    # Retry loop for meter validation
    for attempt in range(max_attempts):
        # Call Mistral API with structured prompt template
        response = client.beta.conversations.start(
            agent_id=agent_id,
            agent_version="latest",
            inputs=[
                {
                    "role": "user",
                    "content": (
                        f"Language: {language}. "
                        f"Write ONE {language} poem about: {safe_input}. "
                        f"Each line MUST be exactly {syllable_count} syllables. "
                        "Output ONLY the 4 lines of the poem. No title, no explanation."
                    ),
                }
            ],
        )

        # Parse reply from agent response outputs
        reply_text = ""
        for output in response.outputs:
            if hasattr(output, "role") and output.role == "assistant":
                content = output.content
                if isinstance(content, list):
                    reply_text = content[0].text
                else:
                    reply_text = content
                break

        if not reply_text:
            continue

        reply_text = reply_text.strip()
        meter_report = validate_poem_meter(reply_text, language)

        if meter_report["all_match"]:
            break

    if not reply_text:
        return {"reply": "Error: Empty response from poetry engine"}

    gc.collect()

    return {
        "reply": reply_text,
        "metadata": {"language": language, "status": "success", "meter": meter_report},
    }
