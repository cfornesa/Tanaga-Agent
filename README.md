# Tanaga Agent (Express + TypeScript)

This project is a Node.js Express migration of the original FastAPI Tanaga app.

## Features

- Same UI/UX and endpoint contract as the previous app
- Mistral Agent integration for poem generation
- Meter validation for Tagalog (7 syllables) and English (8 syllables)
- Localized RAG support using PDF/DOCX files from `documents/`
- On-demand local vector index generation
- Hostinger-compatible build output: `server.bundle.js`

## Required Environment Variables

Create `.env` from `.env.example` and set:

- `NODE_ENV` = `development` or `production`
- `MISTRAL_API_KEY` = your Mistral API key
- `AGENT_ID` = your Mistral Agent ID
- `APP_URL` = your site URL (must be `https://name.tld` format)
- `PORT` = optional, default `5000`

## Local Development

1. Install packages:
   npm install
2. Build local embeddings from `documents/`:
   npm run rag:build
3. Run development server:
   npm run dev

## Production Build

1. Build app:
   npm run build
2. Start server:
   npm start

This produces and runs `server.bundle.js`.

## API Endpoints

- GET `/` serves the chat UI
- GET `/health` returns health metadata
- POST `/generate-tanaga` generates poem output
- GET `/rag/status` returns local index status
- POST `/rag/rebuild` rebuilds local embeddings from `documents/`

## Hostinger Deployment Settings

Use these values in your Node.js app settings:

- Build command: `npm run build`
- Package manager: `npm`
- Entry file: `server.bundle.js`
- Root directory: `./`
- Node version: `20.x`

Set the required environment variables in Hostinger before starting the app.

## Troubleshooting Deploy Builds

If Hostinger shows `esbuild: command not found`, it means the build toolchain was not installed in that deploy environment.

Use this checklist:

- Package manager: `npm`
- Build command: `npm run build`
- Entry file: `server.bundle.js`
- Node version: `20.x`

This repository keeps `esbuild` in `dependencies` so it is available even when production-only installs are used during deploy.
