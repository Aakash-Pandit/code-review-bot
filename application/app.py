import json
import logging
import os

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from application.models.schemas import (
    HealthResponse,
    ChatRequest,
    ChatResponse,
)

logging.getLogger("onnxruntime").setLevel(logging.ERROR)

app = FastAPI(
    title="Code Review Bot API",
    description="API for Code Review Bot powered by Ollama",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")


@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": "Code Review Bot",
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy")


async def stream_llm(prompt: str):
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream(
            "POST",
            f"{OLLAMA_HOST}/api/generate",
            json={"model": "phi3", "prompt": prompt, "stream": True},
        ) as response:
            async for line in response.aiter_lines():
                if line:
                    chunk = json.loads(line)
                    yield chunk.get("response", "")


@app.post("/stream")
async def stream(request: ChatRequest):
    return StreamingResponse(stream_llm(request.query), media_type="text/plain")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(
            f"{OLLAMA_HOST}/api/generate",
            json={"model": "phi3", "prompt": request.query, "stream": False},
        )
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return ChatResponse(query=request.query, answer=response.json()["response"])
