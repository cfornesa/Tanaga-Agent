import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Tanaga Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# GAIL Framework using Docstrings
RULES = """
Write a Tanaga, a Filipino style of poetry, written in the form of four lines written in an A-A-B-B format, where each letter represents a line, and seven total syllables in each line.

- **Structure**: The poem must have exactly four lines.
- **Syllables**: Each line should consist of exactly seven syllables in both English and Tagalog.
- **Language**: Respond in either English or Tagalog, as specified by the user's request.
"""

STEPS = """
1. **Translation**: If necessary, translate the prompt into the target language.
2. **Analysis**: Understand the central theme or concept from the prompt.
3. **Composition**: Write a meaningful and creative poem adhering strictly to the seven-syllables-per-line rule.
"""

OUTPUT_FORMAT = """
Provide the poem in plain text. Ensure each line has exactly seven syllables, and the overall tone matches the theme of the prompt.
"""

SYSTEM_PROMPT = f"{RULES}\n{STEPS}\n{OUTPUT_FORMAT}"

class TanagaRequest(BaseModel):
    user_input: str

@app.post("/generate-tanaga")
async def tanaga_api(req: TanagaRequest):
    client = OpenAI(api_key=os.environ['DEEPSEEK_API_KEY'], base_url="https://api.deepseek.com")
    
    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": req.user_input}
        ]
    )
    
    return {"reply": response.choices[0].message.content}

@app.get("/")
async def root():
    return {"message": "Welcome to Tanaga Agent! Use POST /generate-tanaga to create a Tanaga poem."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
