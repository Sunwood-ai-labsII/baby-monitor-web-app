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
import sys
import time
from dataclasses import dataclass
from typing import Optional

try:
    import cv2  # type: ignore
except ImportError as exc:  # pragma: no cover - OpenCV は外部依存なのでカバレッジ対象外
    raise SystemExit(
        "OpenCV が必要だよ。'python3 -m pip install opencv-python' でインストールしてね。"
    ) from exc


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
    parser = argparse.ArgumentParser(
        description="OpenCV で Tapo C210 の RTSP 映像を視聴するためのツールだよ。"
    )
    parser.add_argument("--host", required=True, help="カメラの IPv4 アドレスまたはホスト名")
    parser.add_argument(
        "--username",
        required=True,
        help="Tapo アプリで設定したカメラアカウントのユーザー名",
    )
    parser.add_argument(
        "--password",
        required=True,
        help="Tapo アプリで設定したカメラアカウントのパスワード",
    )
    parser.add_argument(
        "--stream",
        type=int,
        default=1,
        choices=(1, 2, 6, 7),
        help="RTSP ストリーム番号 (1=メイン HD, 2=サブ, 6/7=デュアルレンズモデル)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=554,
        help="RTSP ポート番号 (既定値 554)",
    )
    parser.add_argument(
        "--reconnect-delay",
        type=float,
        default=DEFAULT_RECONNECT_DELAY,
        help="読み込み失敗後に再接続を試みるまでの待機秒数",
    )
    parser.add_argument(
        "--no-window",
        action="store_true",
        help="ウィンドウを開かず、フレーム情報のログ出力だけ行う",
    )
    parser.add_argument(
        "--frame-log-interval",
        type=int,
        default=60,
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
