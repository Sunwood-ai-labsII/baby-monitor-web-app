# 👶 baby-monitor app (Docker Compose)

RTSP のネットワークカメラ映像を、Docker Compose で HLS/WebRTC に変換してブラウザ再生する最小構成です。

- MediaMTX: RTSP を取り込み、HLS(8888) / WebRTC(8889) で配信
- Nginx: シンプルな HLS プレイヤーの静的ページを配信（ポート 8080）
- Gateway(API): ブラウザからのスナップショットを Gemini で解析（ポート 8081）

## 📦 構成

```
app/
├── docker-compose.yml      # MediaMTX + Nginx
├── mediamtx.yml            # MediaMTXの設定（paths.cam が RTSP をpull）
├── .env.example            # RTSP_URL のサンプル
└── web/
    └── index.html          # HLS プレイヤー（hls.js）
└── gateway/
    ├── Dockerfile          # FastAPI + httpx の軽量ゲートウェイ
    ├── requirements.txt
    └── main.py             # /analyze: 画像+プロンプトを Gemini で解析
```

## 🚀 使い方

1) .env を準備（カメラ情報に置換）

```bash
cd app
cp .env.example .env
# エディタで .env を開き、RTSP_URL を実カメラに合わせて修正
# 例: rtsp://user:pass@192.168.1.123:554/stream1
```

2) 起動

```bash
docker compose up -d
```

3) ブラウザで再生/解析

- HLS プレイヤー: http://localhost:8080/
  - 既定のURL入力: http://localhost:8888/cam/index.m3u8
- WebRTC ビューア（MediaMTX内蔵の簡易UI）: http://localhost:8889/
 - AI 解析（Gemini）: HLS プレイヤー内の「現在のフレームを解析」ボタンをクリック

> HLS は互換性が高く設定も簡単、WebRTC は低遅延です。用途に合わせて選んでください。

## 🔧 設定メモ（MediaMTX）

- `mediamtx.yml` の `paths.cam.source` は `.env` の `RTSP_URL` を読み込みます。
- `sourceOnDemand: yes` により、視聴開始時にカメラへ接続します（無駄な常時接続を回避）。
- CORS を有効化済み（`hlsAllowOrigin: "*"`, `webrtcAllowOrigin: "*"`）。

### Gemini 解析について

- `gateway` サービスは FastAPI で `POST /analyze` を提供し、画像（multipart/form-data, `image`）と任意の `prompt` を受け取って Gemini API に投げます。
- `.env` に `GEMINI_API_KEY` を設定してください（`GEMINI_MODEL` は既定で `gemini-1.5-flash-latest`）。
- ブラウザ側は `video` の現在フレームを `canvas` に描画して JPEG で送信します。

必要に応じてパス名（`cam`）を変えたい場合は、
- `mediamtx.yml` の `paths:` のキー名（`cam`）
- HLS URL（例: `http://localhost:8888/yourpath/index.m3u8`）
の両方を一致させてください。

## 🧪 動作確認のヒント

- Tapo C210 例: `rtsp://<USER>:<PASS>@<CAM_IP>:554/stream1`
- 認証エラーや接続エラー時は `docker compose logs mediamtx` を確認
- 端末から `curl -I http://localhost:8888/cam/index.m3u8` で HLS のヘッダ確認も可
- ゲートウェイの動作確認: `curl -s http://localhost:8081/healthz`

### 内部向けRTSP URL

Docker ネットワーク内のクライアント（将来の Gemini ストリーミング連携サービス等）からは、MediaMTX へ `rtsp://mediamtx:8554/cam` で接続できます。
`example/gemini-realtime-streaming/stream_video.py` をベースに Live API 連携を実装する際の入力として使うと便利です。

## ⚠️ セキュリティ/ネットワーク注意

- ルータのポート開放は原則不要（LAN内視聴）。外部公開する場合は認証/制限の設定を必ず検討してください。
- カメラの認証情報を含む `.env` はコミットしないでください。

---
Happy monitoring 👶📹
