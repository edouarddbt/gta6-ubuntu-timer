#!/usr/bin/env bash
# Uninstallation script for GTA 6 Countdown Timer
set -e

SERVICE_NAME="gta6-timer.service"

echo "🛑 Désinstallation du Timer GTA VI..."

systemctl --user stop "$SERVICE_NAME" 2>/dev/null || true
systemctl --user disable "$SERVICE_NAME" 2>/dev/null || true

rm -f "$HOME/.config/systemd/user/$SERVICE_NAME"
rm -f "$HOME/.local/bin/gta6-timer"
rm -rf "$HOME/.local/share/gta6-timer"
rm -rf "$HOME/.config/gta6-timer"

systemctl --user daemon-reload

echo "✅ Le timer GTA VI a été désinstallé proprement."
