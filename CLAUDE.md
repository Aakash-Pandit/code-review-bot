# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A FastAPI service that proxies chat requests to a locally-running Ollama instance (using the `phi3` model). The stack is Docker Compose: a `fast-api` service, an `ollama` service, and an `ollama-init` service that pulls the model on first run.

## Commands

All primary workflows go through Docker Compose via Make:

```bash
make build      # Build images
make start      # docker-compose up
make stop       # docker-compose down
make rebuild    # stop → build → start
make remove     # stop and remove volumes/orphans
make test       # run pytest inside the fast-api container
```

To run locally without Docker, set `OLLAMA_HOST` to a reachable Ollama instance and start with:

```bash
python main.py
```

The API runs on port `8000` (configurable via `API_PORT` env var). Interactive docs at `/docs`.

## Architecture

```
main.py                         # Entrypoint — reads API_PORT, starts uvicorn
application/
  app.py                        # FastAPI app, CORS middleware, all route handlers
  models/schemas.py             # Pydantic request/response models
compose/Dockerfile              # python:3.11-slim, hot-reload via uvicorn --reload
docker-compose.yml              # fast-api + ollama + ollama-init services
```

**Request flow:** Client → FastAPI (`/chat` or `/stream`) → `httpx` async call → Ollama API (`/api/generate`) → phi3 model.

- `/chat` — collects full response, returns `ChatResponse(query, answer)`
- `/stream` — returns a `StreamingResponse`, streaming tokens as plain text

## Environment Variables

Copy `.env.example` to `.env` before starting:

| Variable | Default | Notes |
|---|---|---|
| `API_PORT` | `8000` | Host port for the FastAPI service |
| `OLLAMA_HOST` | `http://ollama:11434` | Ollama base URL (use `http://localhost:11434` for local dev without Docker) |
