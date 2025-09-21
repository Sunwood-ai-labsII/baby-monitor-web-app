# Gemini リアルタイムストリーミング サンプル

このフォルダには、Google Gemini API をリアルタイムに楽しむサンプルが 2 つ入ってるよ💖

- `stream_text.py` …… REST + SSE でテキストを逐次受信するライトなサンプル
- `stream_video.py` …… Live API (WebSocket) で映像フレームを送り込みながら瞬時に解析してもらうガチ配信モード

## セットアップ

```bash
cd example/gemini-realtime-streaming
uv sync
```

> 💡 `uv` が使えないときは `python3 -m pip install httpx python-dotenv` でも OK。

## `.env` の準備

Gemini API キーなどの秘密情報は `.env` に保存するよ。テンプレをコピーして値を入力してね。

```bash
cd example/gemini-realtime-streaming
cp .env.example .env
# エディタで .env を開き、API キーなどを書き換える
```

利用できる主な環境変数は次のとおり👇

| 変数名 | 必須 | 説明 |
| --- | --- | --- |
| `GEMINI_API_KEY` | ✅ | Google AI Studio などで発行した API キー |
| `GOOGLE_API_KEY` | 任意 | `GEMINI_API_KEY` の代わりに読まれる互換キー名 |
| `GEMINI_MODEL` | 任意 | `stream_text.py` で利用するモデル ID（既定値 `gemini-1.5-flash-latest`） |

## テキストをストリーミングする (SSE)

```bash
cd example/gemini-realtime-streaming
uv run python stream_text.py "子守唄にピッタリの短い詩を書いて"
```

プロンプトをコマンドライン引数で指定しなかった場合は、赤ちゃんの寝かしつけに関する
ヒントを聞く既定のプロンプトで実行するよ。

## 仕組みメモ

- `stream_text.py` は `streamGenerateContent` エンドポイントに `alt=sse` を付けてアクセスしてるよ。
- レスポンスは `data: ...` 形式の SSE チャンクだから、1 行ずつパースしてテキストを組み立ててるの。
- `[DONE]` が届いたらループを抜けてストリームを終了してるよ。

## 映像をリアルタイム解析する (Live API)

ウェブカメラや動画ファイルを投げ込みつつ、Gemini のリアルタイム応答を受け取るには `stream_video.py` を使うよ👇

```bash
cd example/gemini-realtime-streaming
uv run python stream_video.py --source 0
```

主なオプションはこんな感じ！

| オプション | 既定値 | 説明 |
| --- | --- | --- |
| `--source` | `0` | Web カメラ番号、動画ファイル、RTSP URL など好きな映像ソースを指定してね |
| `--model` | `gemini-2.0-flash-live-preview-04-09` | Live API 対応モデル ID |
| `--fps` | `1.0` | 1 秒あたりに送るフレーム数。帯域を抑えたい時は小さめに |
| `--max-width` | `640` | 送信前にリサイズする横幅 (px)。解像度が高すぎる時の保険だよ |
| `--prompt` | 赤ちゃん安全チェックの定型文 | 解析スタート時に送るテキスト指示 |
| `--final-prompt` | 〆のサマリー依頼 | フレーム送信後にまとめてってお願いするテキスト |

実行すると以下の流れで解析が走るよ🌀

1. Live API と接続してシステムプロンプトを設定
2. 最初の `--prompt` をテキストで送信
3. 指定した FPS でフレームを JPEG 化しながら `send_realtime_input(video=...)` で送信
4. モデルから届くコメントは即座に `🤖 Gemini:` 行として出力
5. `--final-prompt` で締めコメントを依頼し、少し待ってから終了

> ⚠️ Web カメラ利用時は `opencv-python-headless` を使っているので GUI ウィンドウは開かないよ。映像プレビューが欲しい場合は別途ビューワーを用意してね。

🚨 API キーは課金対象になるから、実行前に料金設定もチェックしておいてね！
