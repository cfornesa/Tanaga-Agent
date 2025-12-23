import os
import re
import gc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Tanaga Stochastic Engine")

# 1. CORS CONFIGURATION: Bridges Hostinger frontend and Replit backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. PRECISION PRIVACY SCRUBBER: Targets only specific high-risk contact strings.
def redact_pii(text: str) -> str:
    # Thinned regex to avoid redacting Tagalog art words while protecting PII.
    patterns = {
        "EMAIL": r'[\w\.-]+@[\w\.-]+\.\w+',
        "PHONE": r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}'
    }
    for label, pattern in patterns.items():
        text = re.sub(pattern, f"[{label}_REDACTED]", text, flags=re.IGNORECASE)
    return text

# 3. CONSTRAINED GAIL FRAMEWORK (Stochastic Diversification Protocol)
def get_tanaga_system_prompt():
    """
    GOALS: 7-7-7-7 structure with high metaphorical variety (Talinghaga).
    ACTIONS: 
        - VOWEL ANCHOR: Use vowel sounds (A-E-I-O-U) to lock the 7-syllable meter.
        - SYLLABIC CEILING: Forbidden to use words with 4+ syllables.
        - DIVERSIFY: Avoid common cliches (lamig, hangin, langit). Use evocative imagery.
    """
    return (
        "You are a Master of the Traditional Filipino Tanaga. "
        "Each line MUST have exactly 7 vowel sounds.\n\n"
        "STRICT CONSTRAINTS:\n"
        "1. VOWEL COUNT: Exactly 7 per line. Break words into sounds (e.g., 'mga' = ma-nga = 2).\n"
        "2. WORD LIMIT: Do not use words with 4 or more syllables. Use simple but rare root words.\n"
        "3. TALINGHAGA: Do not be literal. Use sensory metaphors (textures, sounds, light, shadow).\n"
        "4. VARIETY: Do not repeat the same poem twice. Explore new word paths.\n\n"
        "OUTPUT: 4 lines only. No analysis."
    )

class PoetryRequest(BaseModel):
    user_input: str
    history: List[Dict] = []

# 4. HEALTH CHECK: Verifies the engine status.
@app.get("/")
async def health():
    return {"status": "Stochastic Engine Online", "meter": "7-7-7-7", "temp": "0.6"}

# 5. MAIN GENERATION ENDPOINT
@app.post("/generate-tanaga")
async def process_chat(request: PoetryRequest):
    from openai import OpenAI

    # Redact input locally for privacy
    safe_input = redact_pii(request.user_input)

    client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

    # Construct strictly constrained message
    messages = [
        {"role": "system", "content": get_tanaga_system_prompt()},
        {"role": "user", "content": f"Theme: {safe_input}"}
    ]

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            # TEMPERATURE 0.6: Forces the model to explore creative metaphors 
            # while the prompt 'anchors' it to the syllabic math.
            temperature=0.6
        )

        reply = response.choices[0].message.content

        # 6. MEMORY MANAGEMENT: Clears RAM to optimize Replit performance.
        del messages, safe_input
        gc.collect()

        return {"reply": reply}
    except Exception as e:
        gc.collect()
        return {"error": f"Generation Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)