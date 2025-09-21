# 👶 赤ちゃん見守り Webアプリ

これは、ネットワークカメラの映像をブラウザで表示して、赤ちゃんを遠隔で見守るためのシンプルなWebアプリケーションです。

## ✨ 機能
- ネットワークカメラのURLを入力して映像を表示
- レスポンシブデザインで、スマートフォンやPCからアクセス可能

## 🚀 使い方

1.  **リポジトリをクローンまたはダウンロードします。**
    ```bash
    git clone https://github.com/Sunwood-ai-labsII/baby-monitor-web-app.git
    ```
2.  **`index.html` をブラウザで開きます。**
    ローカルのファイルを直接開くか、Webサーバー経由でアクセスします。
3.  **カメラのURLを入力します。**
    お使いのネットワークカメラのストリーミングURL（例: `http://192.168.1.100/stream.mjpg`）を入力し、「表示開始」ボタンをクリックします。

## 🔧 セットアップ

このアプリケーションはHTML、CSS、JavaScriptのみで構成されているため、特別なビルドやサーバーサイドのセットアップは不要です。

### ネットワークカメラについて

- このアプリは、`<video>` タグや `<img>` タグで直接表示できるストリーミング形式（MJPEGなど）を想定しています。
- HLS (`.m3u8`) や MPEG-DASH (`.mpd`) などのモダンなストリーミング形式を利用する場合は、`hls.js` や `dash.js` といった追加のJavaScriptライブラリを組み込む必要があります。

## 📹 RTSP録画 (ffmpeg)

RTSPのストリームを短時間キャプチャしてMP4に保存する例です。認証情報やIPは必ず各自の環境に置き換えてください（以下ではマスクしています）。

```bash
ffmpeg -rtsp_transport tcp -i rtsp://<USER>:<PASSWORD>@<CAM_IP>:554/stream1 \
  -t 10 -c:v copy -an -movflags +faststart test.mp4
```

- `-rtsp_transport tcp`: RTSPをTCPで受信（安定性向上）
- `-t 10`: 10秒だけ録画
- `-c:v copy`: 再エンコードせず映像をコピー
- `-an`: 音声を含めない
- `-movflags +faststart`: MP4を先頭最適化（再生開始を高速化）

## 🤝 コントリビュート

改善の提案やプルリクエストをお待ちしています！

## 📄 ライセンス

このプロジェクトは [MIT License](LICENSE) のもとで公開されています。
