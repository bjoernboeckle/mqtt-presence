#!/bin/bash

set -e

SERVICE_NAME="mqtt-presence"
INSTALL_DIR="/opt/$SERVICE_NAME"
SYSTEMD_SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME.service"
CONFIG_PATH="/root/.config/$SERVICE_NAME"
LOG_PATH="/root/.local/state/$SERVICE_NAME"

# Optional: auto-confirmation
if [[ "$1" == "--yes" || "$UNATTENDED" == "1" ]]; then
  CONFIRM="yes"
else
  echo "⚠️  This will remove the service '$SERVICE_NAME', including all related files and configurations."
  read -p "Are you sure? (yes/[no]): " CONFIRM
fi

if [[ "$CONFIRM" != "yes" ]]; then
  echo "Aborted."
  exit 1
fi

echo "[1/4] Stopping and disabling service..."
sudo systemctl stop "$SERVICE_NAME" || true
sudo systemctl disable "$SERVICE_NAME" || true
sudo rm -f "$SYSTEMD_SERVICE_PATH"
sudo systemctl daemon-reload

echo "[2/4] Removing installation..."
sudo rm -rf "$INSTALL_DIR"

echo "[3/4] Deleting configuration..."
sudo rm -rf "$CONFIG_PATH"

echo "[4/4] Deleting logs..."
sudo rm -rf "$LOG_PATH"

echo
echo "✅ Uninstallation completed."
