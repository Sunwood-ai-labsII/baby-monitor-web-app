# Tapo C210 RTSP ビューアサンプル

このフォルダには、TP-Link Tapo C210 ネットワークカメラを RTSP で視聴するための設定手順と、Python 製のサンプルビューアが入っているよ。

## カメラの準備

1. Tapo アプリで専用の **カメラアカウント**（ユーザー名とパスワード）を作成する。手順は *デバイス設定 → 詳細設定 → カメラアカウント* からだよ。これで外部アプリから RTSP でログインできるようになるの。[^tp-link-rtsp]
2. ルーターの DHCP リストや Tapo アプリの *デバイス設定 → デバイス情報* を確認して、カメラの IP アドレスを控えてね。[^tp-link-rtsp]
3. スクリプトを実行するパソコンとカメラが同じネットワーク内で通信できるかチェックしておこう。[^tp-link-rtsp]
4. C210 は少なくとも 2 本の RTSP ストリームを持っているよ。ストリーム 1 が高画質、ストリーム 2 が省帯域モード。ソフトによっては RTSP ポート（既定値 `554`）を URL に含める必要があるから注意してね。[^tp-link-rtsp]

> **RTSP URL 形式:** `rtsp://<カメラアカウントのユーザー名>:<カメラアカウントのパスワード>@<カメラのIP>:554/stream<ストリーム番号>`
>
> `ストリーム番号` にはメイン映像なら `1`、サブストリームなら `2` を指定してね。デュアルレンズモデルでは `stream6` / `stream7` を使う場合があるよ。[^tp-link-rtsp]

## 依存パッケージのインストール

このサンプル用に [uv](https://github.com/astral-sh/uv) を使った仮想環境が用意してあるよ。
以下のコマンドを実行すれば依存関係のインストールと環境構築が一気に完了するの。

```bash
cd example/tapo-rtsp-viewer
uv sync
```

> 💡 もし uv を使わない場合は、`python3 -m pip install opencv-python python-dotenv` でも OK だよ。

## 環境変数 (.env) の設定

カメラの接続情報は `.env` ファイルから読み込むよ。まずはテンプレをコピーして値を埋めてね。

```bash
cd example/tapo-rtsp-viewer
cp .env.example .env
# 好きなエディタで .env を編集して、ホスト名やパスワードを書き換える
```

利用できる主な環境変数はこんな感じ👇

| 変数名 | 必須 | 説明 |
| --- | --- | --- |
| `TAPO_HOST` | ✅ | カメラの IPv4 アドレスまたはホスト名 |
| `TAPO_USERNAME` | ✅ | カメラアカウントのユーザー名 |
| `TAPO_PASSWORD` | ✅ | カメラアカウントのパスワード |
| `TAPO_STREAM` | 任意 | RTSP ストリーム番号（既定値 `1`） |
| `TAPO_PORT` | 任意 | RTSP ポート番号（既定値 `554`） |
| `TAPO_RECONNECT_DELAY` | 任意 | 再接続までに待つ秒数（既定値 `5.0`） |
| `TAPO_NO_WINDOW` | 任意 | `true` にするとフレーム情報のログのみ出力 |
| `TAPO_FRAME_LOG_INTERVAL` | 任意 | ログ出力の間隔となるフレーム数（既定値 `60`） |

ブール値（`TAPO_NO_WINDOW` など）は `true/false` や `1/0`、`yes/no` のような値で指定できるよ。

## ビューアの実行方法

```bash
cd example/tapo-rtsp-viewer
uv run python tapo_c210_rtsp_viewer.py
```

`.env` に書いた値はそのまま使われるよ。必要に応じてコマンドライン引数で上書きすることも可能👇

```bash
uv run python tapo_c210_rtsp_viewer.py --stream 2 --window
```

実行するとライブ映像ウィンドウが開くよ。終了したいときは **Q** キーを押してね。接続が切れても自動的に再接続を試みるから安心。OpenCV がウィンドウを描画できるよう、デスクトップ環境のあるマシン（X11 / Wayland / macOS / Windows など）で動かしてね。

## トラブルシューティングのヒント

* RTSP を試す前に、カメラアカウントの認証情報が Tapo アプリで正しく動くか確認してね。[^tp-link-rtsp]
* 映像が表示されないときは IP アドレスやポート 554、ファイアウォール設定をもう一度チェックしよう。[^tp-link-rtsp]
* TP-Link サポートコミュニティには、RTSP/ONVIF の追加チェック項目がまとまったスレッドがあるから困ったら参照してみて。[^tp-link-community]

[^tp-link-rtsp]: TP-Link, [「How to view Tapo camera on PC/NAS/NVR through RTSP/Onvif Protocol」](https://www.tp-link.com/us/support/faq/2680/)。
[^tp-link-community]: TP-Link Community, [「Tapo Camera RTSP/ONVIF Troubleshooting」](https://community.tp-link.com/en/smart-home/forum/topic/652710)。
