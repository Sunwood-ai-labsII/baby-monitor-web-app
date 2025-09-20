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

Python から映像をデコードするために OpenCV を入れておいてね。

```bash
python3 -m pip install opencv-python
```

## ビューアの実行方法

```bash
python3 example/tapo_c210_rtsp_viewer.py \
    --host 192.168.1.123 \
    --username camera_user \
    --password 'super-secure-password' \
    --stream 1
```

実行するとライブ映像ウィンドウが開くよ。終了したいときは **Q** キーを押してね。接続が切れても自動的に再接続を試みるから安心。OpenCV がウィンドウを描画できるよう、デスクトップ環境のあるマシン（X11 / Wayland / macOS / Windows など）で動かしてね。

## トラブルシューティングのヒント

* RTSP を試す前に、カメラアカウントの認証情報が Tapo アプリで正しく動くか確認してね。[^tp-link-rtsp]
* 映像が表示されないときは IP アドレスやポート 554、ファイアウォール設定をもう一度チェックしよう。[^tp-link-rtsp]
* TP-Link サポートコミュニティには、RTSP/ONVIF の追加チェック項目がまとまったスレッドがあるから困ったら参照してみて。[^tp-link-community]

[^tp-link-rtsp]: TP-Link, [「How to view Tapo camera on PC/NAS/NVR through RTSP/Onvif Protocol」](https://www.tp-link.com/us/support/faq/2680/)。
[^tp-link-community]: TP-Link Community, [「Tapo Camera RTSP/ONVIF Troubleshooting」](https://community.tp-link.com/en/smart-home/forum/topic/652710)。
