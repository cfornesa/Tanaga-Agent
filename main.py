import os
import re
import gc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Tanaga Syllabic Agent")

# 1. CORS CONFIGURATION: Enables the handshake between Hostinger (UI) and Replit (Logic).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. PRIVACY SCRUBBER: Locally sanitizes PII while preserving artistic Tagalog vocabulary.
def redact_pii(text: str) -> str:
    patterns = {
        "EMAIL": r'[\w\.-]+@[\w\.-]+\.\w+',
        "PHONE": r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}'
    }
    for label, pattern in patterns.items():
        text = re.sub(pattern, f"[{label}_REDACTED]", text, flags=re.IGNORECASE)
    return text

# 3. INTEGRATED GAIL FRAMEWORK: The core logic pillars for structural and cultural accuracy.
def get_tanaga_system_prompt():
    """
    GOAL: Generate 7-7-7-7 Tanagas using Few-Shot Anchoring and Syllabic Ceilings.
    ACTION 1 (FEW-SHOT ANCHOR): Provide visual templates to prevent 12-syllable drift.
    ACTION 2 (SYLLABIC CEILING): Forbid words with 4+ syllables to simplify the AI's math.
    INFORMATION: Incorporate Talinghaga (metaphor) to avoid literal 'weather reporting.'
    LANGUAGE: English for explanations; Tagalog/English for poetic output.
    """
    return (
        "You are a Master of the Traditional Filipino Tanaga. "
        "Each line must have exactly 7 vowel sounds (7 syllables).\n\n"
        "CONCEPTUAL IMPLEMENTATION: FEW-SHOT ANCHORS\n"
        "Follow these rhythmic templates precisely:\n"
        "1. Ang la-mig ay du-ma-ting (7)\n"
        "2. Sa Tex-as na lu-pa-in (7)\n"
        "3. Ha-ngin ay u-mi-i-hip (7)\n"
        "4. Ga-bi ay ta-hi-mi-kan (7)\n\n"
        "CONCEPTUAL IMPLEMENTATION: 3-SYLLABLE CEILING\n"
        "- Do not use words like 'nananahimik' or 'bumabalot' (too many syllables).\n"
        "- Use short root words to ensure the 7-syllable count is perfect.\n\n"
        "OUTPUT: 4 lines only. No analysis."
    )

class PoetryRequest(BaseModel):
    user_input: str
    history: List[Dict] = []

# 4. HEALTH CHECK: Verifies the deployment status of the Syllabic Engine.
@app.get("/")
async def health():
    return {"status": "Syllabic Engine Online", "logic": "Few-Shot-Anchored"}

# 5. MAIN GENERATION ENDPOINT: Processes the request with balanced temperature.
@app.post("/generate-tanaga")
async def process_chat(request: PoetryRequest):
    from openai import OpenAI

    # Apply local redaction before hitting the API
    safe_input = redact_pii(request.user_input)

    client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

    # Construct strictly constrained message list
    messages = [
        {"role": "system", "content": get_tanaga_system_prompt()},
        {"role": "user", "content": f"Create a 7-syllable per line Tanaga about: {safe_input}"}
    ]

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            # CONCEPT: TEMPERATURE ANCHORING
            # 0.3 provides enough 'noise' for metaphor without breaking the 7-syllable math.
            temperature=0.3 
        )

        reply = response.choices[0].message.content

        # 6. MEMORY MANAGEMENT: Clears objects to prevent Replit memory leaks.
        del messages, safe_input
        gc.collect()

        return {"reply": reply}
    except Exception as e:
        gc.collect()
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)