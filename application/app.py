import json
import logging
import os

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse

from application.models.schemas import (
    HealthResponse,
    ChatRequest,
    ChatResponse,
    ReviewRequest,
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
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")

_REVIEW_INSTRUCTIONS = {
    "full": "Review the code for bugs and logic errors, security vulnerabilities, performance problems, and readability issues.",
    "security": "Review the code for security vulnerabilities only. Focus on injection risks, insecure data handling, auth issues, and unsafe patterns.",
    "performance": "Review the code for performance problems only. Focus on algorithmic complexity, unnecessary allocations, and bottlenecks.",
    "explain": "Explain what this code does in plain English. Describe its purpose, how it works, and any notable design decisions.",
}


def build_review_prompt(code: str, language: str | None, mode: str | None) -> str:
    mode = mode or "full"
    instructions = _REVIEW_INSTRUCTIONS.get(mode, _REVIEW_INSTRUCTIONS["full"])
    lang_hint = f" The code is written in {language}." if language else ""
    return (
        f"You are a senior software engineer performing a code review.{lang_hint} "
        f"{instructions} "
        "Be specific and reference line numbers where possible. "
        "Format your response with clear sections.\n\n"
        f"Code:\n```\n{code}\n```"
    )


@app.get("/", include_in_schema=False)
async def root():
    return FileResponse("application/static/index.html")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy")


async def stream_llm(prompt: str, model: str):
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream(
            "POST",
            f"{OLLAMA_HOST}/api/generate",
            json={"model": model, "prompt": prompt, "stream": True},
        ) as response:
            async for line in response.aiter_lines():
                if line:
                    chunk = json.loads(line)
                    yield chunk.get("response", "")


@app.post("/stream")
async def stream(request: ChatRequest):
    return StreamingResponse(stream_llm(request.query, OLLAMA_MODEL), media_type="text/plain")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(
            f"{OLLAMA_HOST}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": request.query, "stream": False},
        )
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return ChatResponse(query=request.query, answer=response.json()["response"])


@app.post("/review")
async def review(request: ReviewRequest):
    prompt = build_review_prompt(request.code, request.language, request.mode)
    return StreamingResponse(stream_llm(prompt, OLLAMA_MODEL), media_type="text/plain")
