#!/bin/bash
set -euo pipefail

apt-get update -y
apt-get install -y google-cloud-sdk
apt-get install -y snapd
sudo snap install btop