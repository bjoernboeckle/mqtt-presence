#!/bin/bash

set -e

SERVICE_NAME="mqtt-presence"
INSTALL_DIR="/opt/$SERVICE_NAME"
PYTHON_EXEC="/usr/bin/python3"
VENV_DIR="$INSTALL_DIR/venv"
SYSTEMD_SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME.service"

echo "[1/5] Installing system packages..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

echo "[2/5] Creating virtual environment..."
sudo mkdir -p "$INSTALL_DIR"
sudo python3 -m venv "$VENV_DIR"

echo "[3/5] Installing mqtt-presence..."
sudo $VENV_DIR/bin/pip install --upgrade pip
sudo $VENV_DIR/bin/pip install mqtt-presence

echo "[4/5] Setting up systemd service (as root)..."
sudo tee "$SYSTEMD_SERVICE_PATH" > /dev/null <<EOF
[Unit]
Description=MQTT Presence Service
After=network.target

[Service]
Type=simple
ExecStart=$VENV_DIR/bin/mqtt-presence
WorkingDirectory=$INSTALL_DIR
Restart=on-failure
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

echo "[5/5] Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"
