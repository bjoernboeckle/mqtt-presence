#!/bin/bash
# 'set -e' sorgt dafür, dass das Skript SOFORT abbricht, wenn ein Befehl fehlschlägt.
set -e

SERVICE_NAME="mqtt-presence"
INSTALL_DIR="/opt/$SERVICE_NAME"
CONFIG_PATH="/etc/$SERVICE_NAME"
LOG_PATH="/var/log/$SERVICE_NAME"
VENV_DIR="$INSTALL_DIR/venv"
SYSTEMD_SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME.service"

PIP_OPTS="--timeout 60 --prefer-binary"

echo "[1/5] Installing system packages..."

# 1. Paketmanager-Erkennung über die Existenz der Binaries (viel sicherer für Skripte)
if command -v apt-get &>/dev/null; then
    echo "  → System uses APT (Debian/Ubuntu/Raspberry Pi OS)"
    
    # Listen aktualisieren
    sudo apt-get update -q
    
    echo "  → Installing essential build tools and compiler (SWIG)..."
    # Wir installieren die absolut kritischen Build-Tools zuerst. 
    # Schlägt das fehl, bricht das Skript dank 'set -e' sofort mit echtem Fehler ab.
    sudo apt-get install -y swig build-essential python3-dev liblgpio-dev ca-certificates
    sudo update-ca-certificates

    echo "  → Installing Python environment packages..."
    sudo apt-get install -y python3 python3-pip python3-venv

elif command -v dnf &>/dev/null; then
    echo "  → System uses DNF (Fedora/RHEL)"
    sudo dnf install -y python3 python3-pip python3-devel gcc swig

elif command -v pacman &>/dev/null; then
    echo "  → System uses PACMAN (Arch Linux)"
    sudo pacman -Sy --noconfirm --needed python python-pip gcc swig

elif command -v zypper &>/dev/null; then
    echo "  → System uses ZYPPER (openSUSE)"
    sudo zypper install -y python3 python3-pip python3-venv python3-devel gcc swig
else
    echo "ERROR: No supported package manager found on this system." >&2
    exit 1
fi

# Sicherstellen, dass SWIG jetzt wirklich da ist (Doppelte Absicherung)
if ! command -v swig &>/dev/null; then
    echo "ERROR: 'swig' is missing after APT execution. Installation aborted." >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Virtual Environment erstellen
# ---------------------------------------------------------------------------
echo "[2/5] Creating virtual environment..."
sudo mkdir -p "$INSTALL_DIR"

if [ ! -d "$VENV_DIR" ]; then
    sudo python3 -m venv --system-site-packages "$VENV_DIR"
fi

# ---------------------------------------------------------------------------
# Installation via Pip
# ---------------------------------------------------------------------------
echo "[3/5] Installing or upgrading $SERVICE_NAME inside venv..."

pip_install() {
    local args=("$@")
    if sudo "$VENV_DIR/bin/pip" install $PIP_OPTS "${args[@]}"; then
        return 0
    fi

    echo "  ⚠ Pip failed. Retrying with direct PyPI-only access..."
    sudo PIP_CONFIG_FILE=/dev/null "$VENV_DIR/bin/pip" install \
        $PIP_OPTS \
        --index-url https://pypi.org/simple/ \
        --trusted-host pypi.org \
        --trusted-host files.pythonhosted.org \
        "${args[@]}"
}

pip_install --upgrade pip
pip_install --upgrade "mqtt-presence"

# ---------------------------------------------------------------------------
# Systemd Service einrichten
# ---------------------------------------------------------------------------
echo "[4/5] Creating/updating systemd service..."

SERVICE_CONTENT="[Unit]
Description=MQTT Presence Service
After=network.target

[Service]
Type=simple
ExecStart=$VENV_DIR/bin/mqtt-presence --config $CONFIG_PATH --log $LOG_PATH
WorkingDirectory=$INSTALL_DIR
Restart=on-failure
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
"

if [ ! -f "$SYSTEMD_SERVICE_PATH" ] || ! diff <(echo "$SERVICE_CONTENT") "$SYSTEMD_SERVICE_PATH" > /dev/null; then
    echo "$SERVICE_CONTENT" | sudo tee "$SYSTEMD_SERVICE_PATH" > /dev/null
    echo "  Systemd service file created/updated."
else
    echo "  Systemd service file unchanged."
fi

# ---------------------------------------------------------------------------
# Service starten
# ---------------------------------------------------------------------------
echo "[5/5] Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo ""
echo "✅ Installation successfully completed!"