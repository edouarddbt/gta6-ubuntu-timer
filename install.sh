#!/usr/bin/env bash
# Installation script for GTA 6 Countdown Timer on Ubuntu / GNOME
set -e

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$HOME/.local/share/gta6-timer"
BIN_DIR="$HOME/.local/bin"
SERVICE_DIR="$HOME/.config/systemd/user"

echo "🌴 Installation du Timer GTA VI..."

mkdir -p "$TARGET_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$SERVICE_DIR"

cp "$SRC_DIR/gta6_indicator.py" "$TARGET_DIR/gta6_indicator.py"
chmod +x "$TARGET_DIR/gta6_indicator.py"

cp "$SRC_DIR/gta6-timer" "$BIN_DIR/gta6-timer"
chmod +x "$BIN_DIR/gta6-timer"

cp "$SRC_DIR/gta6-timer.service" "$SERVICE_DIR/gta6-timer.service"

systemctl --user daemon-reload
systemctl --user enable gta6-timer.service
systemctl --user restart gta6-timer.service

echo ""
echo "🎉 Installation réussie !"
echo "👉 Le timer est maintenant visible dans la barre supérieure d'Ubuntu."
echo "👉 Tu peux gérer le timer avec la commande : gta6-timer {start|stop|status|restart}"
