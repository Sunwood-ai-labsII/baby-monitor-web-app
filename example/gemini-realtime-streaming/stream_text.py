"""Gemini API のリアルタイムストリーミング (SSE) サンプルだよ。"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Iterable, Iterator

import httpx
from dotenv import load_dotenv


def _load_dotenv() -> None:
    for candidate in (Path(__file__).with_name(".env"), Path.cwd() / ".env"):
        if candidate.exists():
            load_dotenv(candidate, override=False)


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        raise SystemExit(f"環境変数 {name} が見つからなかったよ。 .env を確認してね。")
    return value.strip()


def _iter_candidate_text(payload: dict) -> Iterator[str]:
    for candidate in payload.get("candidates", []):
        content = candidate.get("content", {})
        parts: Iterable[dict] = content.get("parts", [])
        for part in parts:
            text = part.get("text")
            if isinstance(text, str) and text:
                yield text


def stream_generate_content(prompt: str) -> Iterator[str]:
    _load_dotenv()

    api_key = _require_env("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest").strip() or "gemini-1.5-flash-latest"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent"

    headers = {"Content-Type": "application/json"}
    params = {"alt": "sse", "key": api_key}
    body = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt},
                ],
            }
        ]
    }

    with httpx.Client(timeout=httpx.Timeout(None)) as client:
        with client.stream("POST", url, headers=headers, params=params, json=body) as response:
            response.raise_for_status()
            for raw_line in response.iter_lines():
                if not raw_line:
                    continue
                if raw_line.startswith(":"):
                    # コメント行なのでスルーするよ
                    continue
                if not raw_line.startswith("data:"):
                    continue
                data = raw_line[len("data:") :].strip()
                if data == "[DONE]":
                    break
                try:
                    payload = json.loads(data)
                except json.JSONDecodeError:
                    continue
                yield from _iter_candidate_text(payload)


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    if argv:
        prompt = " ".join(argv)
    else:
        prompt = "赤ちゃんの寝かしつけに役立つ豆知識を教えて"

    try:
        for chunk in stream_generate_content(prompt):
            print(chunk, end="", flush=True)
    except httpx.HTTPStatusError as exc:
        print(f"API からエラーが返ってきたよ: {exc.response.text}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nユーザー操作でストリームを中断したよ。", file=sys.stderr)
    finally:
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
