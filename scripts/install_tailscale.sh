#!/usr/bin/env bash
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "このスクリプトはroot権限で実行してください（例: sudo ./install_tailscale.sh）。"
  exit 1
fi

echo "[1/4] Tailscaleリポジトリの鍵を配置中..."
install -m 0755 -d /usr/share/keyrings
curl -fsSL https://pkgs.tailscale.com/stable/debian/bookworm.noarmor.gpg \
  | tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null

echo "[2/4] aptリポジトリを登録中..."
curl -fsSL https://pkgs.tailscale.com/stable/debian/bookworm.tailscale-keyring.list \
  | tee /etc/apt/sources.list.d/tailscale.list >/dev/null

chmod 0644 /usr/share/keyrings/tailscale-archive-keyring.gpg /etc/apt/sources.list.d/tailscale.list

echo "[3/4] apt更新＆Tailscaleインストール..."
apt-get update
apt-get install -y tailscale tailscale-archive-keyring

echo "[4/4] tailscaledを起動＆自動起動設定..."
systemctl enable --now tailscaled

cat <<'EOF'

=== Tailscale の基本操作 ===
1. Tailnetへログインするには:
   sudo tailscale up
   -> 表示されるURLをブラウザで開き、アカウント連携してください。
2. 状態確認:
   tailscale status
3. SSHも使う場合:
   sudo tailscale up --ssh

インストールとサービス起動は完了しました。認証を実施してTailnetに参加してください。
EOF