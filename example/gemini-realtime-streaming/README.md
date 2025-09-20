# Gemini リアルタイムストリーミング サンプル

このフォルダには、Google Gemini API の `streamGenerateContent` エンドポイントを使って
テキストをストリーミング取得する Python スクリプトが入っているよ。SSE (Server-Sent Events)
でレスポンスを受け取りながら、届いた順に標準出力へ書き出すサンプルだよ。

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
| `GEMINI_MODEL` | 任意 | 利用するモデル ID（既定値 `gemini-1.5-flash-latest`） |

## 実行方法

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

🚨 API キーは課金対象になるから、実行前に料金設定もチェックしておいてね！
