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

# 2. PRIVACY SCRUBBER (PII Redaction)
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

# 3. INTEGRATED GAIL FRAMEWORK (Bilingual Composition Protocol)
def get_tanaga_system_prompt():
    """
    GOALS: Generate authentic Tanagas (4 lines, 7 syllables each) in English OR Tagalog.
    ACTIONS: 
        - LANGUAGE DEFAULT: Respond in English by default. 
        - BILINGUAL COMPOSITION: If requested (or if the prompt is in Tagalog), compose the poem in Tagalog. Otherwise, use English.
        - SYLLABLE STRICTURE: You MUST verify each line has exactly 7 syllables in the chosen language.
    INFORMATION: 
        - Utilize 'Talinghaga' (deep metaphor). 
        - Explain the syllable count and metaphors in English for the user.
    LANGUAGE: 
        - Explanations: English.
        - Poem: Context-dependent (English or Tagalog).
    """
    return (
        "You are a Master of the Traditional Filipino Tanaga. You are bilingual in English and Tagalog.\n\n"
        "GOALS:\n"
        "Create a 4-line poem with exactly 7 syllables per line. Default to English unless Tagalog is requested.\n\n"
        "ACTIONS:\n"
        "1. POEM LANGUAGE: You are permitted and encouraged to write the poem in Tagalog if the user asks. If no language is specified, use English.\n"
        "2. VERIFICATION: List the syllable count for each line to prove the 7-7-7-7 structure.\n"
        "3. TALINGHAGA: Provide a brief English explanation of the metaphors used.\n\n"
        "INFORMATION:\n"
        "The Tanaga is a heritage form. Respect its history of AAAA or AABB rhyme schemes.\n\n"
        "LANGUAGE:\n"
        "Explanations MUST be in English. The poem follows user preference."
    )

class PoetryRequest(BaseModel):
    user_input: str
    history: List[Dict] = []

# 4. HEALTH CHECK
@app.get("/")
async def health():
    return {"status": "Bilingual Tanaga Agent Online", "mode": "7-7-7-7-Strict"}

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
            temperature=0.6 # Reduced slightly for better syllable counting accuracy
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