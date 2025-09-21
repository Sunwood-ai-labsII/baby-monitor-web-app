from __future__ import annotations

import base64
import os
from typing import Optional

import httpx
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest").strip() or "gemini-1.5-flash-latest"

app = FastAPI(title="Gemini Gateway", version="0.1.0")

# Allow cross-origin from local dev hosts by default
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze_image(
    image: UploadFile = File(...),
    prompt: Optional[str] = Form(None),
):
    if not GEMINI_API_KEY:
        return {"error": "GEMINI_API_KEY is not configured in environment"}

    # Default prompt focuses on baby monitoring safety cues
    prompt = (prompt or "赤ちゃんの安全や快適さの観点で、気づいた点を日本語で簡潔に箇条書きしてください。")[:2000]

    content = await image.read()
    b64 = base64.b64encode(content).decode("ascii")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

    body = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": image.content_type or "image/jpeg",
                            "data": b64,
                        }
                    },
                    {"text": prompt},
                ],
            }
        ]
    }

    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}

    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        r = await client.post(url, headers=headers, params=params, json=body)
        try:
            r.raise_for_status()
        except httpx.HTTPStatusError:
            return {"error": "gemini_api_error", "status": r.status_code, "body": r.text}
        data = r.json()

    # Try to extract plain text
    text = ""
    for cand in (data.get("candidates") or []):
        content = cand.get("content") or {}
        for part in (content.get("parts") or []):
            t = part.get("text")
            if isinstance(t, str):
                text += t

    return {"model": GEMINI_MODEL, "text": text.strip(), "raw": data}

