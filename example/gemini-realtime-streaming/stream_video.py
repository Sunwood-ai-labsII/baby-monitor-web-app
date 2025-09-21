"""Gemini Live API を使って映像をリアルタイム解析するサンプルだよ💫"""
from __future__ import annotations

import argparse
import asyncio
import contextlib
import os
import sys
from pathlib import Path
from typing import Any, AsyncIterator, Optional, Tuple

import cv2
from dotenv import load_dotenv
from google import genai
from google.genai import types


DEFAULT_MODEL = "gemini-2.0-flash-live-preview-04-09"


def _load_dotenv() -> None:
    for candidate in (Path(__file__).with_name(".env"), Path.cwd() / ".env"):
        if candidate.exists():
            load_dotenv(candidate, override=False)


def _require_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise SystemExit("GEMINI_API_KEY か GOOGLE_API_KEY を .env に設定してね💡")
    return api_key.strip()


def _resolve_source(raw: str) -> int | str:
    try:
        return int(raw)
    except ValueError:
        return raw


def _open_capture(source: int | str) -> cv2.VideoCapture:
    capture = cv2.VideoCapture(source)
    if not capture.isOpened():
        raise SystemExit(f"映像ソース {source!r} を開けなかったよ💦")
    return capture


async def _iter_frames(
    capture: cv2.VideoCapture,
    *,
    target_fps: float,
    max_frames: Optional[int],
    max_width: Optional[int],
) -> AsyncIterator[Tuple[int, Any]]:
    interval = 1.0 / target_fps if target_fps > 0 else 0.0
    frame_index = 0
    try:
        while True:
            ok, frame = await asyncio.to_thread(capture.read)
            if not ok:
                break
            frame_index += 1
            if max_frames is not None and frame_index > max_frames:
                break
            if max_width and frame.shape[1] > max_width:
                scale = max_width / frame.shape[1]
                new_size = (int(frame.shape[1] * scale), int(frame.shape[0] * scale))
                frame = await asyncio.to_thread(cv2.resize, frame, new_size)
            yield frame_index, frame
            if interval > 0:
                await asyncio.sleep(interval)
    finally:
        capture.release()


async def _send_video_frames(
    session: genai.aio.live.AsyncSession,
    capture: cv2.VideoCapture,
    *,
    target_fps: float,
    max_frames: Optional[int],
    max_width: Optional[int],
    jpeg_quality: int,
) -> None:
    params = [int(cv2.IMWRITE_JPEG_QUALITY), int(jpeg_quality)]
    async for frame_index, frame in _iter_frames(
        capture,
        target_fps=target_fps,
        max_frames=max_frames,
        max_width=max_width,
    ):
        success, encoded = await asyncio.to_thread(cv2.imencode, ".jpg", frame, params)
        if not success:
            print(f"⚠️ フレーム {frame_index} のエンコードに失敗したよ", file=sys.stderr)
            continue
        blob = types.Blob(data=encoded.tobytes(), mime_type="image/jpeg")
        await session.send_realtime_input(video=blob)
        print(f"📤 フレーム {frame_index} を送信中…", end="\r", flush=True)
    print()


async def _receive_loop(session: genai.aio.live.AsyncSession) -> None:
    try:
        async for message in session.receive():
            if message.setup_complete:
                print("✅ Gemini がリアルタイム準備OKだよ〜✨")
                continue

            if message.server_content and message.server_content.model_turn:
                parts = message.server_content.model_turn.parts or []
                for part in parts:
                    if part.text:
                        print(f"\n🤖 Gemini: {part.text}")

            if message.usage_metadata:
                usage = message.usage_metadata
                prompt_tokens = usage.prompt_token_count or 0
                response_tokens = usage.candidates_token_count or 0
                print(
                    f"\n📊 Token usage → prompt: {prompt_tokens}, response: {response_tokens}"
                )
    except asyncio.CancelledError:
        pass


async def _amain(args: argparse.Namespace) -> None:
    _load_dotenv()
    api_key = _require_api_key()
    source = _resolve_source(args.source)
    capture = _open_capture(source)

    client = genai.Client(api_key=api_key, http_options={"api_version": "v1alpha"})
    system_instruction = args.system_instruction.strip() if args.system_instruction else ""
    config = types.LiveConnectConfig(
        response_modalities=["TEXT"],
        system_instruction=types.Content(
            parts=[types.Part(text=system_instruction or "映像から重要ポイントを即座に伝えてね。")]
        ),
        generation_config=types.GenerationConfig(
            temperature=args.temperature,
            top_p=args.top_p,
            max_output_tokens=args.max_output_tokens,
        ),
    )

    async with client.aio.live.connect(model=args.model, config=config) as session:
        receiver = asyncio.create_task(_receive_loop(session))

        prompt = args.prompt.strip()
        if prompt:
            await session.send_realtime_input(text=prompt)

        await _send_video_frames(
            session,
            capture,
            target_fps=args.fps,
            max_frames=args.max_frames,
            max_width=args.max_width,
            jpeg_quality=args.jpeg_quality,
        )

        final_prompt = args.final_prompt.strip()
        if final_prompt:
            await session.send_realtime_input(text=final_prompt)

        await asyncio.sleep(args.response_grace)
        receiver.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await receiver


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gemini Live API で映像をストリーミング解析するよ",
    )
    parser.add_argument(
        "--source",
        default="0",
        help="映像ソース。Webカメラ番号 (例: 0) か動画ファイル/RTSP URL を指定してね",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"使うモデル ID (既定: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=1.0,
        help="1 秒あたりの送信フレーム数。帯域を節約したいときは小さくしてね",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        help="送信する最大フレーム数。指定しない場合は映像が終わるまで送るよ",
    )
    parser.add_argument(
        "--max-width",
        type=int,
        default=640,
        help="フレームの最大横幅 (px)。縮小して帯域を抑えたいときに使ってね",
    )
    parser.add_argument(
        "--jpeg-quality",
        type=int,
        default=80,
        help="JPEG 品質 (0-100)。数値が高いほど高画質だけどデータ量も増えるよ",
    )
    parser.add_argument(
        "--prompt",
        default="赤ちゃんの安全や快適さに関わるポイントをリアルタイムで教えて",
        help="最初に送る指示テキスト",
    )
    parser.add_argument(
        "--final-prompt",
        default="これで映像の送信はおしまい！直近の気づきを手短にまとめてね✨",
        help="フレーム送信後に送る締めのテキスト",
    )
    parser.add_argument(
        "--response-grace",
        type=float,
        default=5.0,
        help="最後の応答を待つ秒数",
    )
    parser.add_argument(
        "--system-instruction",
        default="赤ちゃんモニターの安全管理アシスタントとして、危険や異常を素早く指摘して。",
        help="システムプロンプトに設定する文章",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.4,
        help="生成温度。小さくすると安定、大きくすると多様性アップだよ",
    )
    parser.add_argument(
        "--top-p",
        type=float,
        default=0.8,
        help="top-p サンプリングのしきい値",
    )
    parser.add_argument(
        "--max-output-tokens",
        type=int,
        default=512,
        help="モデルの最大出力トークン数",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    try:
        asyncio.run(_amain(args))
    except KeyboardInterrupt:
        print("\n⏹️ ユーザー操作でストリーミングを終了したよ", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
