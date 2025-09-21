"""TP-Link Tapo C210 から 1 枚だけスナップショットを保存する簡易スクリプトだよ。

このスクリプトは OpenCV（`opencv-python`）と `python-dotenv` が必要。

使用例
------

1) .env を使う（`TAPO_HOST`, `TAPO_USERNAME`, `TAPO_PASSWORD` を設定しておく）

```bash
uv run python tapo_c210_snapshot.py --output snapshot.jpg
```

2) 直接引数で指定する

```bash
python3 tapo_c210_snapshot.py \
  --host 192.168.1.123 \
  --username camera_user \
  --password "strong-password" \
  --stream 1 \
  --output snapshot_$(date +%Y%m%d_%H%M%S).jpg
```
"""
from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import cv2  # type: ignore
except ImportError as exc:  # pragma: no cover - OpenCV は外部依存
    raise SystemExit(
        "OpenCV が必要だよ。'uv sync' で環境構築するか、'python3 -m pip install opencv-python' でインストールしてね。"
    ) from exc

from dotenv import load_dotenv


def _load_default_env() -> None:
    """カレントディレクトリとスクリプト直下の `.env` を読み込むよ。"""

    for candidate in (Path(__file__).with_name(".env"), Path.cwd() / ".env"):
        if candidate.exists():
            load_dotenv(candidate, override=False)


_load_default_env()


DEFAULT_STREAM = 1
DEFAULT_PORT = 554
DEFAULT_WARMUP_FRAMES = 5  # 保存前に捨てるフレーム数（露光など安定待ち）


@dataclass
class SnapshotConfig:
    host: str
    username: str
    password: str
    stream: int = DEFAULT_STREAM
    port: int = DEFAULT_PORT
    output: Path = Path("snapshot.jpg")
    warmup_frames: int = DEFAULT_WARMUP_FRAMES

    def rtsp_url(self) -> str:
        return f"rtsp://{self.username}:{self.password}@{self.host}:{self.port}/stream{self.stream}"

    def safe_display_target(self) -> str:
        return f"rtsp://{self.host}:{self.port}/stream{self.stream}"


def parse_args(argv: Optional[list[str]] = None) -> SnapshotConfig:
    def _optional_str(name: str) -> Optional[str]:
        value = os.getenv(name)
        if value is None:
            return None
        value = value.strip()
        return value or None

    def _optional_int(name: str) -> Optional[int]:
        v = _optional_str(name)
        if v is None:
            return None
        try:
            return int(v)
        except ValueError as exc:
            raise SystemExit(f"環境変数 {name} の値 '{v}' を整数に変換できなかったよ。") from exc

    env_defaults = {
        "host": _optional_str("TAPO_HOST"),
        "username": _optional_str("TAPO_USERNAME"),
        "password": _optional_str("TAPO_PASSWORD"),
        "stream": _optional_int("TAPO_STREAM"),
        "port": _optional_int("TAPO_PORT"),
        # 任意: 保存先（指定がなければ自動で日付入りファイル名を作る）
        "output": _optional_str("TAPO_SNAPSHOT_PATH"),
        "warmup": _optional_int("TAPO_WARMUP_FRAMES"),
    }

    default_stream = env_defaults["stream"] if env_defaults["stream"] is not None else DEFAULT_STREAM
    default_port = env_defaults["port"] if env_defaults["port"] is not None else DEFAULT_PORT
    default_warmup = env_defaults["warmup"] if env_defaults["warmup"] is not None else DEFAULT_WARMUP_FRAMES

    # 出力ファイルのデフォルト: snapshot_YYYYmmdd_HHMMSS.jpg
    default_output = env_defaults["output"]
    if not default_output:
        default_output = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

    parser = argparse.ArgumentParser(description="Tapo C210 から 1 枚だけ画像を保存するツールだよ。")
    parser.add_argument("--host", required=env_defaults["host"] is None, default=env_defaults["host"], help="カメラの IPv4 アドレスまたはホスト名")
    parser.add_argument("--username", required=env_defaults["username"] is None, default=env_defaults["username"], help="カメラアカウントのユーザー名")
    parser.add_argument("--password", required=env_defaults["password"] is None, default=env_defaults["password"], help="カメラアカウントのパスワード")
    parser.add_argument("--stream", type=int, default=default_stream, choices=(1, 2, 6, 7), help="RTSP ストリーム番号 (1=メイン HD, 2=サブ, 6/7=デュアルレンズ)")
    parser.add_argument("--port", type=int, default=default_port, help="RTSP ポート番号 (既定値 554)")
    parser.add_argument("--output", type=Path, default=Path(default_output), help="保存する画像のパス (.jpg/.png など)")
    parser.add_argument("--warmup-frames", type=int, default=default_warmup, help="保存前に捨てるフレーム数（露光や AWB の安定待ち）")

    args = parser.parse_args(argv)
    return SnapshotConfig(
        host=args.host,
        username=args.username,
        password=args.password,
        stream=args.stream,
        port=args.port,
        output=args.output,
        warmup_frames=args.warmup_frames,
    )


def open_capture(url: str) -> Optional["cv2.VideoCapture"]:
    cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        cap.release()
        return None
    # 遅延を減らすため、可能ならバッファ小さめ
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap


def take_snapshot(config: SnapshotConfig) -> None:
    url = config.rtsp_url()
    print(f"{config.safe_display_target()!r} に接続して 1 枚だけ保存するよ…")

    cap = open_capture(url)
    if cap is None:
        raise SystemExit("RTSP ストリームを開けなかったよ。IP・認証情報・RTSP 設定を確認してね。")

    try:
        # ウォームアップ: 指定枚数だけ読み飛ばし
        for _ in range(max(0, config.warmup_frames)):
            ok, _ = cap.read()
            if not ok:
                raise SystemExit("フレームを読み取れなかったよ。接続や認証情報を確認してね。")

        ok, frame = cap.read()
        if not ok or frame is None:
            raise SystemExit("フレームを取得できなかったよ。もう一度試してみてね。")

        # 保存先ディレクトリを用意
        config.output.parent.mkdir(parents=True, exist_ok=True)

        ext = config.output.suffix.lower()
        out_path = config.output if ext else config.output.with_suffix(".jpg")

        # JPEG のときは品質を高めに（90）
        jpeg_params: list[int] = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

        success = False
        # まずは通常の imwrite を試す
        try:
            if out_path.suffix.lower() in {".jpg", ".jpeg"}:
                success = bool(cv2.imwrite(str(out_path), frame, jpeg_params))
            else:
                success = bool(cv2.imwrite(str(out_path), frame))
        except Exception:
            success = False

        # 失敗したら、Windows の一部環境での非 ASCII パス対策として imencode + tofile で再試行
        if not success:
            encode_ext = out_path.suffix.lower() or ".jpg"
            params: list[int] = jpeg_params if encode_ext in {".jpg", ".jpeg"} else []
            enc_ok, buf = cv2.imencode(encode_ext, frame, params)
            if enc_ok:
                try:
                    buf.tofile(str(out_path))  # numpy.ndarray.tofile は戻り値 None（例外出なければ OK）
                    success = out_path.exists() and out_path.stat().st_size > 0
                except Exception:
                    success = False

        if not success:
            raise SystemExit(f"画像の保存に失敗したよ: {out_path}")

        print(f"保存したよ: {out_path.resolve()}")
    finally:
        cap.release()


def main(argv: Optional[list[str]] = None) -> int:
    cfg = parse_args(argv)
    try:
        take_snapshot(cfg)
    except KeyboardInterrupt:
        print("ユーザー操作で中断されたよ。")
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
