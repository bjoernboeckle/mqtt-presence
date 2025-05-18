
# mqtt-presence

[![PyPI version](https://badge.fury.io/py/mqtt-presence.svg)](https://badge.fury.io/py/mqtt-presence)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) 
[![Build](https://github.com/bjoernboeckle/mqtt-presence/actions/workflows/ci.yml/badge.svg)](https://github.com/bjoernboeckle/mqtt-presence/actions)

<img src="docs/images/logo.png" alt="mqtt_presence logo" width="128">

**mqtt-presence** is a lightweight Python-based presence indicator for MQTT systems. Originally designed for Raspberry Pi environments, it now supports Windows, Linux. It reports the online status of a device (e.g., a PC) and listens for shutdown or restart commands.  
It is especially useful in smart home environments such as [Home Assistant](https://www.home-assistant.io/).

---

## ✨ Features

- Publishes device online state to MQTT  
- Receives shutdown and restart commands via MQTT  
- Supports Home Assistant MQTT Discovery (optional)  
- Cross-platform: Windows, Linux  
- Provides Web UI and Console UI  
- Configuration via YAML and JSON files  

---

## 🚀 Getting Started

### 📦 Installation

#### Windows

> **Note:** Installation and uninstallation require Administrator rights.

##### Install

```powershell
iwr -useb https://raw.githubusercontent.com/bjoernboeckle/mqtt-presence/main/scripts/install.ps1 | iex
```

##### Uninstall

```powershell
iwr -useb https://raw.githubusercontent.com/bjoernboeckle/mqtt-presence/main/scripts/uninstall.ps1 | iex
```

---

#### Linux

##### Install

```bash
curl -sSL "https://raw.githubusercontent.com/bjoernboeckle/mqtt-presence/main/scripts/install.sh?$(date +%s)" | bash
```

##### Uninstall

```bash
curl -sSL "https://raw.githubusercontent.com/bjoernboeckle/mqtt-presence/main/scripts/uninstall.sh?$(date +%s)" | bash -s -- --yes
```

---

#### As Python Package

Install via pip:

```bash
pip install mqtt-presence
```

Run with default Web UI:

```bash
mqtt-presence
```

Run with Console UI:

```bash
mqtt-presence --ui console
```

Run as Python module:

```bash
python -m mqtt_presence.main
```

---

#### As Executable

Download the latest executable from the [GitHub releases](https://github.com/bjoernboeckle/mqtt-presence/releases) page.

Run:

```bash
mqtt-presence.exe
```

---

## ⚙️ Command Line Options

```bash
mqtt-presence.exe --ui webui      # Starts the Web UI (default)
mqtt-presence.exe --ui console    # Starts the Console UI
```

---

## 📟 Web UI

Access the Web UI in your browser at:

```
http://<ip-address>:8000
```

Example: [http://localhost:8000](http://localhost:8000)

<img src="docs/images/mqtt-presence-webui.png" alt="mqtt_presence Web UI screenshot" width="800">

---

## 🛠 Configuration

Configuration files are created on first run.

### `config.yaml` (Application Settings)

```yaml
app:
  disableShutdown: false         # Set to true to disable shutdown commands (for testing)
mqtt:
  client_id: mqtt-presence_PC    # MQTT client ID (must be unique)
webServer:
  host: 0.0.0.0                  # Host IP for the Web UI
  port: 8000                     # Port for the Web UI
```

Changes require a restart of the service.

### `config.json` (Runtime State)

Managed by the Web UI. Manual edits are overwritten on save.

---

## 📁 Directory Structure

### Installation paths used by scripts:

| OS        | Paths                                                                                  |
|-----------|----------------------------------------------------------------------------------------|
| **Linux** | Install: `/opt/mqtt_presence` <br> Data: `/etc/mqtt_presence` <br> Logs: `/var/log`    |
| **Windows** | Install: `%ProgramData%\mqtt_presence` <br> Data: `%ProgramData%\mqtt_presence\data` <br> Logs: `%ProgramData%\mqtt_presence\log` |

---

### Default Config/Data Paths

| OS        | Config Path                                 |
|-----------|---------------------------------------------|
| Linux     | `~/.config/mqtt_presence/config.yaml`       |
| Windows   | `%APPDATA%\mqtt_presence\config.yaml`       |
| macOS     | `~/Library/Application Support/mqtt_presence/config.yaml` |

---

### Default Log Paths

| OS        | Log Path                                   |
|-----------|---------------------------------------------|
| Linux     | `~/.local/state/mqtt_presence/app.log`      |
| Windows   | `%LOCALAPPDATA%\mqtt_presence\Logs\app.log` |
| macOS     | `~/Library/Logs/mqtt_presence/app.log`      |

---

### Cache Paths

| OS        | Cache Path                                |
|-----------|--------------------------------------------|
| Linux     | `~/.cache/mqtt_presence/status.cache`      |
| Windows   | `%LOCALAPPDATA%\mqtt_presence\Cache\status.cache` |
| macOS     | `~/Library/Caches/mqtt_presence/status.cache` |

---

## 📦 Build and Deploy

### Python Package

```bash
pip install --upgrade build
make build

pip install --upgrade twine
twine upload dist/*
```

### Executable (PyInstaller)

With spec file:

```bash
python -m PyInstaller mqtt-presence.spec
```

Without spec file:

```bash
python -m PyInstaller --onefile --name mqtt-presence mqtt_presence/main.py
```

---

## 🧠 License & Credits

Licensed under the Apache License 2.0. Developed by [Bjoern Boeckle](https://github.com/bjoernboeckle).  
Special thanks to the Home Assistant community for inspiration and support.
