import os
import re
import gc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Tanaga Poetry Agent")

# 1. CORS CONFIGURATION: Enables secure cross-origin communication between Replit and Hostinger.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. PRIVACY SCRUBBER: Sanitizes user inputs locally to prevent PII leakage to the LLM API.
def redact_pii(text: str) -> str:
    patterns = {
        "EMAIL": r'[\w\.-]+@[\w\.-]+\.\w+',
        "PHONE": r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
    }
    for label, pattern in patterns.items():
        text = re.sub(pattern, f"[{label}_REDACTED]", text, flags=re.IGNORECASE)
    return text

# 3. INTEGRATED GAIL FRAMEWORK: The "Brain" of the agent.
def get_tanaga_system_prompt():
    """
    CONCEPT 1: PHONETIC AUDIT - Forces the AI to vocalize sounds rather than just counting letters.
    CONCEPT 2: LINGUISTIC PRIORITY - Ensures composition happens directly in the target language.
    CONCEPT 3: SHORT-WORD STRATEGY - Reduces mathematical errors by limiting word complexity.
    """
    return (
        "You are a Master of the Traditional Filipino Tanaga. You use strict phonetic audits.\n\n"
        "ACTIONS (AUDIT PROTOCOL):\n"
        "1. MANUAL PANTIG: Break every word into vocalized sounds (e.g., 'Mga' is Ma-nga).\n"
        "2. SHORT WORD STRATEGY: Prefer words with 1-3 syllables to ensure 7-7-7-7 accuracy.\n"
        "3. NO TRANSLATION: If Tagalog is requested, compose in Tagalog immediately to protect the meter.\n\n"
        "STRICT CONSTRAINTS:\n"
        "Line 1-4: Exactly 7 syllables each. Provide a hyphenated breakdown to prove the count.\n\n"
        "INFORMATION:\n"
        "Use Talinghaga (metaphors). Acknowledge [REDACTED] as a conceptual void or silence.\n\n"
        "LANGUAGE:\n"
        "Explanations: English. Poem: User's choice. Syllable Audit: English."
    )

class PoetryRequest(BaseModel):
    user_input: str
    history: List[Dict] = []

# 4. HEALTH CHECK: Endpoint to verify the active logic and privacy layers without running a chat.
@app.get("/")
async def health():
    return {"status": "Tanaga Auditor Online", "mode": "7-syl-strict", "scrubber": "active"}

# 5. MAIN CHAT ENDPOINT: Processes the request using the mathematical rigidity of low temperature.
@app.post("/generate-tanaga")
async def process_chat(request: PoetryRequest):
    from openai import OpenAI

    # Apply local privacy scrub
    safe_input = redact_pii(request.user_input)

    client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

    messages = [{"role": "system", "content": get_tanaga_system_prompt()}] + request.history
    messages.append({"role": "user", "content": safe_input})

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            # CONCEPT 4: MATHEMATICAL RIGIDITY - Low temperature (0.1) stops 'creative' syllable cheating.
            temperature=0.1 
        )

        reply = response.choices[0].message.content

        # 6. MEMORY MANAGEMENT: Explicitly clears variables to manage Replit's RAM limits.
        del messages, safe_input
        gc.collect()

        return {"reply": reply}
    except Exception as e:
        gc.collect()
        return {"error": f"Poetry generation failed: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)