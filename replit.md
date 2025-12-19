# Tanaga Agent

## Overview
A FastAPI application that generates Tanaga poems (Filipino poetry) using the DeepSeek Reasoner model. The app accepts user input and creates a four-line poem with seven syllables per line in an A-A-B-B rhyme scheme.

## Project Structure
- `main.py` - FastAPI application with the `/generate-tanaga` endpoint

## API Endpoints
- `GET /` - Welcome message
- `POST /generate-tanaga` - Generate a Tanaga poem (requires `user_input` in request body)

## Dependencies
- FastAPI
- Uvicorn
- OpenAI (for DeepSeek API compatibility)
- Pydantic

## Environment Variables
- `DEEPSEEK_API_KEY` - Required for accessing the DeepSeek Reasoner model

## Deployment
Configured for autoscale deployment on Replit.
