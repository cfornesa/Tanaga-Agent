import os
import re
import gc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Tanaga Poetry Agent")

# 1. CORS CONFIGURATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. PRIVACY SCRUBBER (Redacts PII locally)
def redact_pii(text: str) -> str:
    patterns = {
        "EMAIL": r'[\w\.-]+@[\w\.-]+\.\w+',
        "PHONE": r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
        "SSN": r'\b(?!666|000|9\d{2})\d{3}[- ]?(?!00)\d{2}[- ]?(?!0000)\d{4}\b',
        "ADDRESS": r'\d{1,5}\s\w+.\s(\b\w+\b\s){1,2}\w+,\s\w+,\s[A-Z]{2}\s\d{5}'
    }
    for label, pattern in patterns.items():
        text = re.sub(pattern, f"[{label}_REDACTED]", text, flags=re.IGNORECASE)
    return text

# 3. INTEGRATED GAIL FRAMEWORK (Phonetic Audit Protocol)
def get_tanaga_system_prompt():
    """
    GOALS: Generate structurally perfect Tanagas (4 lines, 7 syllables each).
    ACTIONS: 
        - PHONETIC AUDIT: You must break every word into syllables before writing.
        - TAGALOG PHONETICS: 'Mga' is 2 syllables (ma-nga). 'Sa ilalim' is 4 syllables (sa i-la-lim).
        - SYLLABLE MANDATE: Every line MUST have exactly 7 syllables.
        - LINGUISTIC PRIORITY: Compose directly in Tagalog if requested; do not translate from English.
    INFORMATION: 
        - Use traditional 'Talinghaga' (metaphor) to represent the user's theme.
    LANGUAGE: 
        - Poem: Tagalog or English as requested.
        - Explanations & Audit: English.
    """
    return (
        "You are a Master of the Traditional Filipino Tanaga. You are a strict phonetic auditor.\n\n"
        "ACTIONS (AUDIT PROTOCOL):\n"
        "1. MANUAL PANTIG: You must break down every word by its vocalized sounds.\n"
        "   Example: 'Mga' is ma-nga (2). 'Araw' is a-raw (2).\n"
        "2. ZERO TOLERANCE: Any line that is not exactly 7 syllables is a failure. Rewrite until perfect.\n"
        "3. STRUCTURE: Provide the hyphenated breakdown for each line to prove the count.\n\n"
        "INFORMATION:\n"
        "Incorporate Talinghaga (metaphor). If the user uses [REDACTED], treat it as a void.\n\n"
        "LANGUAGE:\n"
        "Explanations and Syllable Counts MUST be in English. The poem follows user preference.\n"
        "STRICTLY ENGLISH FOR THE AUDIT SECTION."
    )

class PoetryRequest(BaseModel):
    user_input: str
    history: List[Dict] = []

# 4. HEALTH CHECK
@app.get("/")
async def health():
    return {"status": "Tanaga Auditor Agent Online", "mode": "Phonetic-Audit-Enabled"}

# 5. MAIN CHAT ENDPOINT
@app.post("/generate-tanaga")
async def process_chat(request: PoetryRequest):
    from openai import OpenAI

    # Redact input locally
    safe_input = redact_pii(request.user_input)

    client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

    messages = [{"role": "system", "content": get_tanaga_system_prompt()}] + request.history
    messages.append({"role": "user", "content": safe_input})

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            # Temperature 0.2 is essential for mathematical accuracy in syllable counting
            temperature=0.2
        )

        reply = response.choices[0].message.content

        # 6. MEMORY MANAGEMENT
        del messages, safe_input
        gc.collect()

        return {"reply": reply}
    except Exception as e:
        gc.collect()
        return {"error": f"Poetry process interrupted: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)