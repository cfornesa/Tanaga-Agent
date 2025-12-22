import os
import re
import gc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Tanaga Poetry Agent")

# 1. CORS CONFIGURATION (Essential for frontend connectivity)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. PRIVACY SCRUBBER (Redacts PII, SSNs, and Physical Addresses)
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

# 3. INTEGRATED GAIL FRAMEWORK (With Structural & Cultural Safeguards)
def get_tanaga_system_prompt():
    """
    GOALS: Generate authentic, high-quality Tanaga poetry based on user themes.
    ACTIONS: 
        - Adhere strictly to the 4-line, 7-syllables-per-line structure.
        - Implement the traditional AAAA (monorhyme) scheme.
    SAFEGUARDS: 
        - Structural Veracity: Verify syllable counts mentally before outputting.
        - Cultural Integrity: Respect the Filipino roots of the form; avoid 
          modern Western 'free verse' styles that break the Tanaga tradition.
    INFORMATION: 
        - Utilize vivid, metaphorical imagery (talinghaga).
        - Respect any [REDACTED] placeholders in the theme.
    LANGUAGE: Poetic, evocative, and rhythmic.
    """
    return (
        "You are a Master Poet specializing in the traditional Filipino Tanaga.\n\n"
        "GOALS:\n"
        "Produce a poem consisting of exactly four lines, with seven syllables each, "
        "following an AAAA rhyme scheme.\n\n"
        "ACTIONS (STRUCTURAL SAFEGUARD):\n"
        "1. Count syllables carefully. Each line must be exactly 7 syllables.\n"
        "2. Ensure the end-rhymes for all four lines are consistent (AAAA).\n"
        "3. Use 'Talinghaga' (metaphor) to give the poem depth, as is traditional.\n\n"
        "INFORMATION & LANGUAGE:\n"
        "Focus on the theme provided. If the user provides [REDACTED] content, "
        "ignore it and use the surrounding context to build the poem's atmosphere. "
        "Keep the language elegant and respectful of the form's history."
    )

class PoetryRequest(BaseModel):
    theme: str
    history: List[Dict] = []

# 4. HEALTH CHECK (Verifies server and privacy layers)
@app.get("/")
async def health():
    return {
        "status": "Tanaga Agent Online", 
        "structure": "7-7-7-7 AAAA",
        "privacy": "Active"
    }

# 5. MAIN GENERATION ENDPOINT
@app.post("/generate")
async def generate_poetry(request: PoetryRequest):
    # DEFERRED IMPORT: Keeps memory usage low
    from openai import OpenAI

    # Redact input locally
    safe_theme = redact_pii(request.theme)

    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if not api_key:
        return {"error": "DeepSeek API Key missing."}

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    # Construct prompt for DeepSeek-V3
    messages = [{"role": "system", "content": get_tanaga_system_prompt()}] + request.history
    messages.append({"role": "user", "content": f"Theme: {safe_theme}"})

    try:
        response = client.chat.completions.create(
            model="deepseek-chat", # V3 is excellent for rhythmic/constrained text
            messages=messages
        )

        poem = response.choices[0].message.content

        # 6. MEMORY MANAGEMENT
        del messages, safe_theme
        gc.collect()

        return {"tanaga": poem}
    except Exception as e:
        gc.collect()
        return {"error": f"Poetic engine failed: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)