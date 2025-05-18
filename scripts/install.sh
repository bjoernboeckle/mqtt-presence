#!/bin/bash

set -e  # stop in case of errors

SERVICE_NAME="mqtt-presence"
INSTALL_DIR="/opt/$SERVICE_NAME"
DATA_PATH="/etc/$SERVICE_NAME"
LOG_PATH="/var/log/$SERVICE_NAME"
VENV_DIR="$INSTALL_DIR/venv"
SYSTEMD_SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME.service"

echo "[1/5] Installing system packages..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

echo "[2/5] Creating virtual environment (if not exists)..."
if [ ! -d "$VENV_DIR" ]; then
    sudo mkdir -p "$INSTALL_DIR"
    sudo python3 -m venv "$VENV_DIR"
fi

echo "[3/5] Installing or upgrading mqtt-presence..."
sudo "$VENV_DIR/bin/pip" install --upgrade pip
sudo "$VENV_DIR/bin/pip" install --upgrade mqtt-presence


echo "[4/5] Creating/updating systemd service..."
SERVICE_CONTENT="[Unit]
Description=MQTT Presence Service
After=network.target

[Service]
Type=simple
ExecStart=$VENV_DIR/bin/mqtt-presence --data $DATA_PATH --log $LOG_PATH
WorkingDirectory=$INSTALL_DIR
Restart=on-failure
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
"

# Schreibe Service-Datei nur wenn sich Inhalt ändert (optional)
if [ ! -f "$SYSTEMD_SERVICE_PATH" ] || ! diff <(echo "$SERVICE_CONTENT") "$SYSTEMD_SERVICE_PATH" > /dev/null; then
    echo "$SERVICE_CONTENT" | sudo tee "$SYSTEMD_SERVICE_PATH" > /dev/null
    echo "Systemd service file created/updated."
else
    echo "Systemd service file unchanged."
fi

echo "[5/5] Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo "✅ Done. Service is running. Use 'systemctl status $SERVICE_NAME' to check status."
