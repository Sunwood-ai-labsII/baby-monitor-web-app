"""TP-Link Tapo C210 を RTSP で視聴するためのシンプルなビューアだよ。

このスクリプトは OpenCV（``opencv-python`` パッケージ）が必要。ライブ映像を表示するならデスクトップ環境で実行してね。

使用例
------

```bash
python3 tapo_c210_rtsp_viewer.py \
    --host 192.168.1.123 \
    --username camera_user \
    --password "strong-password" \
    --stream 1
```

OpenCV のウィンドウで ``Q`` キーを押すか、ターミナルで ``Ctrl+C`` を押すと終了できるよ。
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    import cv2  # type: ignore
except ImportError as exc:  # pragma: no cover - OpenCV は外部依存なのでカバレッジ対象外
    raise SystemExit(
        "OpenCV が必要だよ。'uv sync' で環境構築するか、'python3 -m pip install opencv-python' でインストールしてね。"
    ) from exc

from dotenv import load_dotenv


def _load_default_env() -> None:
    """カレントディレクトリとスクリプト直下の ``.env`` を読み込むよ。"""

    for candidate in (Path(__file__).with_name(".env"), Path.cwd() / ".env"):
        if candidate.exists():
            load_dotenv(candidate, override=False)


_load_default_env()


DEFAULT_RECONNECT_DELAY = 5.0
WINDOW_TITLE = "Tapo C210 Live"


@dataclass
class ViewerConfig:
    host: str
    username: str
    password: str
    stream: int = 1
    port: int = 554
    reconnect_delay: float = DEFAULT_RECONNECT_DELAY
    no_window: bool = False
    frame_log_interval: int = 60

    def rtsp_url(self) -> str:
        return f"rtsp://{self.username}:{self.password}@{self.host}:{self.port}/stream{self.stream}"


def parse_args(argv: Optional[list[str]] = None) -> ViewerConfig:
    def _optional_str(name: str) -> Optional[str]:
        value = os.getenv(name)
        if value is None:
            return None
        value = value.strip()
        return value or None

    def _optional_int(name: str) -> Optional[int]:
        value = _optional_str(name)
        if value is None:
            return None
        try:
            return int(value)
        except ValueError as exc:
            raise SystemExit(f"環境変数 {name} の値 '{value}' を整数に変換できなかったよ。") from exc

    def _optional_float(name: str) -> Optional[float]:
        value = _optional_str(name)
        if value is None:
            return None
        try:
            return float(value)
        except ValueError as exc:
            raise SystemExit(f"環境変数 {name} の値 '{value}' を数値に変換できなかったよ。") from exc

    def _optional_bool(name: str) -> Optional[bool]:
        value = _optional_str(name)
        if value is None:
            return None
        lowered = value.lower()
        if lowered in {"1", "true", "t", "yes", "y", "on"}:
            return True
        if lowered in {"0", "false", "f", "no", "n", "off"}:
            return False
        raise SystemExit(
            f"環境変数 {name} には true/false を表す値を入れてね。受け付けるのは"
            " 1/0, true/false, yes/no, on/off のみだよ。"
        )

    env_defaults = {
        "host": _optional_str("TAPO_HOST"),
        "username": _optional_str("TAPO_USERNAME"),
        "password": _optional_str("TAPO_PASSWORD"),
        "stream": _optional_int("TAPO_STREAM"),
        "port": _optional_int("TAPO_PORT"),
        "reconnect_delay": _optional_float("TAPO_RECONNECT_DELAY"),
        "no_window": _optional_bool("TAPO_NO_WINDOW"),
        "frame_log_interval": _optional_int("TAPO_FRAME_LOG_INTERVAL"),
    }

    default_stream = env_defaults["stream"] if env_defaults["stream"] is not None else 1
    default_port = env_defaults["port"] if env_defaults["port"] is not None else 554
    default_reconnect_delay = (
        env_defaults["reconnect_delay"] if env_defaults["reconnect_delay"] is not None else DEFAULT_RECONNECT_DELAY
    )
    default_frame_log_interval = (
        env_defaults["frame_log_interval"] if env_defaults["frame_log_interval"] is not None else 60
    )
    default_no_window = env_defaults["no_window"] if env_defaults["no_window"] is not None else False

    parser = argparse.ArgumentParser(
        description="OpenCV で Tapo C210 の RTSP 映像を視聴するためのツールだよ。"
    )
    parser.add_argument(
        "--host",
        required=env_defaults["host"] is None,
        default=env_defaults["host"],
        help="カメラの IPv4 アドレスまたはホスト名",
    )
    parser.add_argument(
        "--username",
        required=env_defaults["username"] is None,
        default=env_defaults["username"],
        help="Tapo アプリで設定したカメラアカウントのユーザー名",
    )
    parser.add_argument(
        "--password",
        required=env_defaults["password"] is None,
        default=env_defaults["password"],
        help="Tapo アプリで設定したカメラアカウントのパスワード",
    )
    parser.add_argument(
        "--stream",
        type=int,
        default=default_stream,
        choices=(1, 2, 6, 7),
        help="RTSP ストリーム番号 (1=メイン HD, 2=サブ, 6/7=デュアルレンズモデル)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=default_port,
        help="RTSP ポート番号 (既定値 554)",
    )
    parser.add_argument(
        "--reconnect-delay",
        type=float,
        default=default_reconnect_delay,
        help="読み込み失敗後に再接続を試みるまでの待機秒数",
    )
    parser.set_defaults(no_window=default_no_window)
    parser.add_argument(
        "--no-window",
        dest="no_window",
        action="store_true",
        help="ウィンドウを開かず、フレーム情報のログ出力だけ行う",
    )
    parser.add_argument(
        "--window",
        dest="no_window",
        action="store_false",
        help="環境変数で no-window が有効なときでもウィンドウを開くよ",
    )
    parser.add_argument(
        "--frame-log-interval",
        type=int,
        default=default_frame_log_interval,
        help="指定したフレーム数ごとにステータスを表示",
    )

    args = parser.parse_args(argv)
    return ViewerConfig(
        host=args.host,
        username=args.username,
        password=args.password,
        stream=args.stream,
        port=args.port,
        reconnect_delay=args.reconnect_delay,
        no_window=args.no_window,
        frame_log_interval=args.frame_log_interval,
    )


def open_capture(url: str) -> Optional["cv2.VideoCapture"]:
    capture = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
    if not capture.isOpened():
        capture.release()
        return None

    # バックエンドが対応していればバッファを縮めて遅延を減らすよ。
    capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return capture


def view_stream(config: ViewerConfig) -> None:
    frame_count = 0
    url = config.rtsp_url()
    print(f"{url!r} に接続中だよ")

    while True:
        capture = open_capture(url)
        if capture is None:
            print(
                "RTSP ストリームを開けなかったよ。IP・認証情報・RTSP 設定を確認してね。"
            )
            time.sleep(config.reconnect_delay)
            continue

        try:
            while True:
                ok, frame = capture.read()
                if not ok:
                    print("カメラとの接続が切れたよ。再接続を試みるね。")
                    break

                frame_count += 1
                if config.no_window:
                    if frame_count % config.frame_log_interval == 0:
                        h, w = frame.shape[:2]
                        print(f"{frame_count} フレーム読み込んだよ（最新フレームのサイズ: {w}x{h}）")
                else:
                    cv2.imshow(WINDOW_TITLE, frame)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        print("終了リクエストを受け取ったよ。ビューアを閉じるね。")
                        return
        except KeyboardInterrupt:
            print("ユーザー操作で中断されたよ。ビューアを閉じるね。")
            return
        finally:
            capture.release()
            if not config.no_window:
                cv2.destroyWindow(WINDOW_TITLE)

        time.sleep(config.reconnect_delay)


def main(argv: Optional[list[str]] = None) -> int:
    config = parse_args(argv)
    try:
        view_stream(config)
    except KeyboardInterrupt:
        print("ユーザー操作で中断されたよ。ビューアを閉じるね。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
