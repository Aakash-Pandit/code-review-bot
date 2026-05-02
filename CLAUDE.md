# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A FastAPI service that acts as a code review bot backed by a locally-running Ollama instance (`qwen2.5-coder:7b`). Users paste code into the web UI, pick a review mode, and get streaming feedback. The stack is Docker Compose: a `fast-api` service, an `ollama` service, and an `ollama-init` service that pulls the model on first run.

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
main.py                              # Entrypoint — reads API_PORT, starts uvicorn
application/
  app.py                             # FastAPI app, all route handlers, stream_llm(), build_review_prompt()
  models/schemas.py                  # Pydantic models: ChatRequest/Response, ReviewRequest, HealthResponse
  static/index.html                  # Single-page frontend (no build step)
compose/Dockerfile                   # python:3.11-slim, hot-reload via uvicorn --reload
docker-compose.yml                   # fast-api + ollama + ollama-init services
```

**Core review flow:** `POST /review` → `build_review_prompt()` constructs a system prompt → `stream_llm()` streams tokens from Ollama → `StreamingResponse` sends them to the client.

**Review modes** (`mode` field on `ReviewRequest`): `full`, `security`, `performance`, `explain`.

The frontend at `/` uses `fetch()` + `ReadableStream` to consume the streaming response and render it incrementally. Cmd/Ctrl+Enter submits.

## Environment Variables

Copy `.env.example` to `.env` before starting:

| Variable | Default | Notes |
|---|---|---|
| `API_PORT` | `8000` | Host port for the FastAPI service |
| `OLLAMA_HOST` | `http://ollama:11434` | Ollama base URL (use `http://localhost:11434` for local dev without Docker) |
| `OLLAMA_MODEL` | `qwen2.5-coder:7b` | Ollama model name — change to swap models without code edits |
