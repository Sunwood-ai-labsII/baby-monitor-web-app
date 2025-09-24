#!/bin/bash
# create-swap-10G.sh
# Ubuntuで10GBのスワップ領域を作成・設定するスクリプト

set -e

SWAPFILE="/swapfile"
SIZE="10G"

echo "[1/5] スワップファイルを作成中: $SWAPFILE ($SIZE)"
sudo fallocate -l $SIZE $SWAPFILE || {
  echo "fallocate が使えない場合、以下を試してください:"
  echo "sudo dd if=/dev/zero of=$SWAPFILE bs=1M count=10240 status=progress"
  exit 1
}

echo "[2/5] 権限を設定中..."
sudo chmod 600 $SWAPFILE

echo "[3/5] スワップ領域として初期化中..."
sudo mkswap $SWAPFILE

echo "[4/5] スワップを有効化中..."
sudo swapon $SWAPFILE

echo "[5/5] /etc/fstab に追加して永続化..."
if ! grep -q "$SWAPFILE" /etc/fstab; then
  echo "$SWAPFILE none swap sw 0 0" | sudo tee -a /etc/fstab
fi

echo "✅ スワップの設定が完了しました！"
echo "現在のスワップ領域:"
swapon --show
free -h
