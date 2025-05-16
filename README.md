
# mqtt_presence


[![PyPI version](https://badge.fury.io/py/mqtt-presence.svg)](https://badge.fury.io/py/mqtt-presence)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Build](https://github.com/bjoernboeckle/mqtt-presence/actions/workflows/build.yml/badge.svg)](https://github.com/bjoernboeckle/mqtt-presence/actions)



<img src="docs/images/logo.png" alt="mqtt_presence logo" style="width:128px;">

**mqtt-presence** is a lightweight Python-based presence indicator for MQTT systems.  
Originally designed for Raspberry Pi environments, it now supports Windows, Linux, and macOS systems alike.  
It reports the online status of a device (like a PC) and receives shutdown or restart commands.  
It's especially useful in smart home environments such as [Home Assistant](https://www.home-assistant.io/).

---



## ✨ Features

- Publishes online state to MQTT
- Receives shutdown and restart commands from MQTT
- Supports Home Assistant MQTT discovery (optional)
- Works on Windows, Linux, and macOS
- Includes Web UI and Console UI options
- Configuration via YAML and JSON

---

## 🚀 Getting Started

### 📦 Installation

### Windows

Install / uninstall need to run with admin rights.

#### Install:

```powershell
iwr -useb https://raw.githubusercontent.com/bjoernboeckle/mqtt-presence/main/install/install.ps1 | iex
```

#### Uninstall:

```powershell
iwr -useb https://raw.githubusercontent.com/bjoernboeckle/mqtt-presence/main/install/uninstall.ps1 | iex
```

### Linux

#### Install:

```bash
curl -sSL "https://raw.githubusercontent.com/bjoernboeckle/mqtt-presence/main/install/install.sh?$(date +%s)" | bash
```


#### Uninstall:

```bash
curl -sSL "https://raw.githubusercontent.com/bjoernboeckle/mqtt-presence/main/install/uninstall.sh?$(date +%s)" | bash -s -- --yes
```

### As Python Package

Install via pip:

```bash
pip install mqtt-presence
```

Run:

```bash
mqtt-presence
```

With console UI:

```bash
mqtt-presence --ui console
```

As Python module:

```bash
python -m mqtt_presence.main
```

#### As Executable

Download and run the executable:

https://github.com/bjoernboeckle/mqtt-presence/releases

```bash
mqtt-presence.exe
```

---

## ⚙️ Command Line Options

```bash
mqtt-presence.exe --ui webui      # Starts the web UI (default)
mqtt-presence.exe --ui console    # Starts the console UI
```

---

## 📟 WebUI

The web ui can be opened by ip adress and default port 8000.

    Example: http://localhost:8000


<img src="docs/images/mqtt-presence-webui.png" alt="mqtt_presence logo" style="width:800px;">


---


## 🛠 Configuration

Configuration files are created on first start.

### `config.yaml` (App Settings)

```yaml
app:
  disableShutdown: false         # Set to true to disable shutdown for testing
mqtt:
  client_id: mqtt-presence_PC    # MQTT client ID (should be unique)
webServer:
  host: 0.0.0.0                  # Host for web UI
  port: 8000                     # Port for web UI
```

Changes require restart.

### `config.json` (Runtime State)

Edited via the web UI. Manual changes are overwritten.

---

## 📁 Directory Structure

### Configuration Files

| OS          | Path                                                  |
|-------------|-------------------------------------------------------|
| **Windows** | `%APPDATA%\mqtt_presence\config.yaml`              |
| **Linux**   | `~/.config/mqtt_presence/config.yaml`                |
| **macOS**   | `~/Library/Application Support/mqtt_presence/`       |

### Log Files

| OS          | Path                                                  |
|-------------|-------------------------------------------------------|
| **Windows** | `%LOCALAPPDATA%\mqtt_presence\Logs\app.log`       |
| **Linux**   | `~/.local/state/mqtt_presence/app.log`               |
| **macOS**   | `~/Library/Logs/mqtt_presence/app.log`               |

### Cache

| OS          | Path                                                    |
|-------------|---------------------------------------------------------|
| **Windows** | `%LOCALAPPDATA%\mqtt_presence\Cache\status.cache`   |
| **Linux**   | `~/.cache/mqtt_presence/status.cache`                  |
| **macOS**   | `~/Library/Caches/mqtt_presence/status.cache`          |



---

## 📦 Build and Deploy

### Python Package

```bash
pip install --upgrade build
python -m build

pip install --upgrade twine
twine upload dist/*
```

### Executable (PyInstaller)

With spec:

```bash
python -m PyInstaller mqtt-presence.spec
```

Without spec:

```bash
python -m PyInstaller --onefile --name mqtt-presence mqtt_presence/main.py
```

---

## 🧠 License & Credits

Apache License. Developed by [Bjoern Boeckle](https://github.com/bjoernboeckle).  
Special thanks to the Home Assistant community.

