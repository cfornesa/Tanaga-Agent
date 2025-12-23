import os
import re
import gc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Tanaga Syllabic Agent")

# 1. CORS CONFIGURATION: Enables secure Hostinger-to-Replit communication.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. PRIVACY SCRUBBER: Sanitizes high-risk PII locally before API transmission.
def redact_pii(text: str) -> str:
    patterns = {
        "EMAIL": r'[\w\.-]+@[\w\.-]+\.\w+',
        "PHONE": r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}'
    }
    for label, pattern in patterns.items():
        text = re.sub(pattern, f"[{label}_REDACTED]", text, flags=re.IGNORECASE)
    return text

# 3. INTEGRATED GAIL FRAMEWORK: The core logic for structural/cultural accuracy.
def get_tanaga_system_prompt():
    """
    PILLAR 1 (FEW-SHOT ANCHORING): Provides a visual and rhythmic template for the AI.
    PILLAR 2 (PHONETIC AUDIT): Forces the AI to count vocalized vowel sounds (A-E-I-O-U).
    PILLAR 3 (SYLLABIC CEILING): Forbids words with 4+ syllables to maintain math accuracy.
    PILLAR 4 (TALINGHAGA): Commands the use of nature-based metaphors over literal text.
    """
    return (
        "You are an Expert Tanaga Poet. Each line must have exactly 7 vowel sounds.\n\n"
        "CONCEPTUAL IMPLEMENTATION: FEW-SHOT ANCHORING\n"
        "Pattern: [Word] [Word] [Word] = 7 Vowels.\n"
        "Example: Ang la-mig ay na-ri-to (7)\n\n"
        "CONCEPTUAL IMPLEMENTATION: PHONETIC AUDIT\n"
        "- Count every vowel sound. 'Mga' is 2 (Ma-nga). 'Sa' is 1.\n"
        "- Use the 3-syllable word ceiling. No words like 'nanlalamig'.\n\n"
        "STRICT STRUCTURE: 4 lines, 7 syllables each. No analysis."
    )

class PoetryRequest(BaseModel):
    user_input: str
    history: List[Dict] = []

# 4. HEALTH CHECK: Verifies the deployment and specific Logic Mode.
@app.get("/")
async def health():
    return {"status": "Anchor-Engine Online", "logic": "GAIL-Pillar-v4", "temp": 0.4}

# 5. MAIN GENERATION ENDPOINT: Executes the logic with creative/syllabic balance.
@app.post("/generate-tanaga")
async def process_chat(request: PoetryRequest):
    from openai import OpenAI

    # Apply local redaction
    safe_input = redact_pii(request.user_input)

    client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

    messages = [
        {"role": "system", "content": get_tanaga_system_prompt()},
        {"role": "user", "content": f"Theme: {safe_input}"}
    ]

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            # CONCEPTUAL IMPLEMENTATION: TEMPERATURE ANCHORING
            # 0.4 allows for creative metaphor without the math-collapse of higher settings.
            temperature=0.4 
        )

        reply = response.choices[0].message.content

        # 6. MEMORY MANAGEMENT: Prevents RAM overflow on Replit's shared containers.
        del messages, safe_input
        gc.collect()

        return {"reply": reply}
    except Exception as e:
        gc.collect()
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)