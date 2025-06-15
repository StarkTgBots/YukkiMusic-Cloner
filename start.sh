#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "🔹 Updating package list..."
apt-get -yq update

echo "🔹 Downloading Google Chrome..."
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O google-chrome-stable_current_amd64.deb

echo "🔹 Installing Google Chrome..."
apt-get -yq install -y --no-install-recommends ./google-chrome-stable_current_amd64.deb

echo "✅ Google Chrome installed successfully!"
google-chrome --version

echo "Installing FFmpeg..."
apt-get install -y ffmpeg

echo "Pip Installing..."

pip3 install -r requirements.txt

echo "Starting..."
python3 -m YukkiMusic