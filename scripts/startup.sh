#!/bin/bash
set -euo pipefail

apt-get update -y
apt-get install -y google-cloud-sdk
apt-get install -y snapd
snap install btop

curl -fsSL https://raw.githubusercontent.com/Sunwood-ai-labs/AMATERASU/refs/heads/main/scripts/docker-compose_setup_script.sh | sudo bash -s --

curl -fsSL https://raw.githubusercontent.com/Sunwood-ai-labsII/baby-monitor-web-app/refs/heads/develop/scripts/create-swap-10G.sh | sudo bash -s --
