"""
main.py – FastAPI application entry point for the Tanaga & Poetry Agent.

Configures the app, registers middleware, defines routes, and delegates
all core logic to tanaga.py.
"""

import os
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


# Import the core poem generation function from model.py
from model import generate_poem

# Operational Transparency Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instantiate FastAPI object
app = FastAPI(
    title="Tanaga & Poetry Agent - Meter Corrected Edition",
    description="Generates poetry with strict meter adherence",
    version="9.6"
)

# CORS Middleware: allow cross-origin access for UI clients.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static files
app.mount("/static", StaticFiles(directory="static"), name="static")


class PoetryRequest(BaseModel):
    """Request model for Tanaga/poetry generation."""
    user_input: str
    language: str = "Tagalog"  # Default to Tagalog
    history: List[Dict] = []



# Serve the frontend
@app.get("/")
async def index():
    return FileResponse("templates/index.html")

# Health check route
@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "version": "9.6",
        "features": [
            "strict_meter_enforcement",
            "cultural_authenticity",
            "deterministic_generation"
        ]
    }

# Poetry generation route
# Expected fields: user_input (str) and optional history (list)
@app.post("/generate-tanaga")
async def generate_poetry(request: PoetryRequest):
    """
    Accept a user poetry request and return a meter-validated poem.

    Delegates all generation and validation logic to tanaga.generate_poem.
    """
    try:
        result = generate_poem(request.user_input, request.language)
        return result
    except Exception as e:
        return {"reply": f"System Error: {str(e)}"}



# Ensures the uvicorn dev server runs when the file is executed directly
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
