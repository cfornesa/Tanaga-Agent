import os
import gc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Tanaga Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. HEALTH CHECK (Existing, kept clean)
@app.get("/")
async def root():
    return {"message": "Welcome to Tanaga Agent! Use POST /generate-tanaga to create a Tanaga poem."}

class TanagaRequest(BaseModel):
    user_input: str

# 2. DEFERRED SYSTEM PROMPT
def get_tanaga_prompt():
    # Only exists in RAM when poetry is being generated
    RULES = """Write a Tanaga...""" # (Your full rules)
    STEPS = """1. Translation...""" # (Your full steps)
    OUTPUT_FORMAT = """Provide the poem...""" # (Your full output format)
    return f"{RULES}\n{STEPS}\n{OUTPUT_FORMAT}"

@app.post("/generate-tanaga")
async def tanaga_api(req: TanagaRequest):
    # 3. DEFERRED IMPORT
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ['DEEPSEEK_API_KEY'], 
        base_url="https://api.deepseek.com"
    )

    system_prompt = get_tanaga_prompt()

    try:
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.user_input}
            ]
        )

        reply = response.choices[0].message.content

        # 4. CLEANUP
        gc.collect()

        return {"reply": reply}
    except Exception as e:
        gc.collect()
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)