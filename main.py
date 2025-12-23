import os
import re
import gc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Tanaga Syllabic Engine v4")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def redact_pii(text: str) -> str:
    patterns = {
        "EMAIL": r'[\w\.-]+@[\w\.-]+\.\w+',
        "PHONE": r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}'
    }
    for label, pattern in patterns.items():
        text = re.sub(pattern, f"[{label}_REDACTED]", text, flags=re.IGNORECASE)
    return text

def get_tanaga_system_prompt():
    """
    CONCEPT: SELF-CORRECTION LOOP.
    The AI is now instructed to count vowels twice: once during writing, 
    and once during a 'Refinement' phase.
    """
    return (
        "You are a Master of the Traditional Filipino Tanaga. "
        "Each line must have exactly 7 vowel sounds.\n\n"
        "STRICT CONSTRAINTS:\n"
        "1. NO LONG WORDS: Words with 4+ syllables (like 'naninipi' or 'bumabalot') are FORBIDDEN.\n"
        "2. VOWEL COUNT: Count the vowel sounds (A, E, I, O, U). \n"
        "3. THE RE-READ: If a line feels long, shorten it. 'Ang lupa ay nanigidig' (8) is WRONG. 'Lupa ay nanigas na' (7) is RIGHT.\n"
        "4. VARIETY: Use new metaphors (smoke, ash, glass, bone).\n\n"
        "OUTPUT: 4 lines only. Be 100% sure of the 7-syllable count before responding."
    )

class PoetryRequest(BaseModel):
    user_input: str
    history: List[Dict] = []

@app.post("/generate-tanaga")
async def process_chat(request: PoetryRequest):
    from openai import OpenAI
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
            temperature=0.6 # The creative sweet spot
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