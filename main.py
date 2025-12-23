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

# 3. INTEGRATED GAIL FRAMEWORK (Dynamic Linguistic Priority)
def get_tanaga_system_prompt():
    """
    GOALS: Generate authentic Tanagas (4 lines, 7 syllables each) with strict phonetic counts.
    ACTIONS: 
        - DYNAMIC PRIORITY: 
            * If Tagalog is requested/used: Compose DIRECTLY in Tagalog (Tagalog-First). Do not translate.
            * If English is requested/used: Compose DIRECTLY in English (English-First).
        - SYLLABLE MANDATE: Verify 7 syllables per line based on vocalized sounds in the active language.
        - VERIFICATION: Provide a manual syllable breakdown (e.g., ma-la-mig = 3).
    INFORMATION: 
        - Use 'Talinghaga' (metaphor). Acknowledge [REDACTED] as a stylistic void.
    LANGUAGE: 
        - Explanations: English.
        - Poem: Based on Dynamic Priority.
    """
    return (
        "You are a Master of the Traditional Filipino Tanaga. You use Dynamic Linguistic Priority.\n\n"
        "ACTIONS (PHONETIC PROTOCOL):\n"
        "1. COMPOSITION MODE: If the prompt is in Tagalog or asks for Tagalog, you MUST think and compose "
        "directly in Tagalog. Never translate from English to Tagalog for the poem, as it breaks syllable counts.\n"
        "2. MANUAL PANTIG: Break words into sounds. In Tagalog, CV (Consonant-Vowel) is the unit. "
        "Example: 'u-mi-i-yak' is 4 syllables. 'ngu-nit' is 2.\n"
        "3. RHYME: Maintain AAAA or AABB rhyme schemes.\n\n"
        "STRICT STRUCTURE:\n"
        "Line 1: 7 syllables\n"
        "Line 2: 7 syllables\n"
        "Line 3: 7 syllables\n"
        "Line 4: 7 syllables\n\n"
        "LANGUAGE: Explanations in English only. Poem follows user preference."
    )

class PoetryRequest(BaseModel):
    user_input: str
    history: List[Dict] = []

# 4. HEALTH CHECK (Verifies Phonetic-First Mode)
@app.get("/")
async def health():
    return {"status": "Tanaga Agent Online", "mode": "Dynamic-Linguistic-Priority-Active"}

# 5. MAIN CHAT ENDPOINT
@app.post("/generate-tanaga")
async def process_chat(request: PoetryRequest):
    from openai import OpenAI
    safe_input = redact_pii(request.user_input)
    client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

    messages = [{"role": "system", "content": get_tanaga_system_prompt()}] + request.history
    messages.append({"role": "user", "content": safe_input})

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            # Lower temperature (0.4) ensures strict mathematical syllable counting
            temperature=0.4
        )
        reply = response.choices[0].message.content
        del messages, safe_input
        gc.collect()
        return {"reply": reply}
    except Exception as e:
        gc.collect()
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)