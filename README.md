
# mqtt-presence

[![PyPI version](https://badge.fury.io/py/mqtt-presence.svg)](https://badge.fury.io/py/mqtt-presence)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) 
[![Build](https://github.com/bjoernboeckle/mqtt-presence/actions/workflows/ci.yml/badge.svg)](https://github.com/bjoernboeckle/mqtt-presence/actions)

<img src="docs/images/logo.png" alt="mqtt_presence logo" width="128">

**mqtt-presence** is a lightweight Python-based presence indicator for MQTT systems. Originally designed for Raspberry Pi environments, it now supports Windows, Linux. It reports the online status of a device (e.g., a PC) and listens for shutdown or restart commands.  
It is especially useful in smart home environments such as [Home Assistant](https://www.home-assistant.io/) in combination with a mqtt broker.

---

## ✨ Features

- Publishes device online state and other pc information to MQTT  
- Receives shutdown and restart commands via MQTT  
- Supports Home Assistant MQTT Discovery (optional)
- Allows configuration of RaspberryPI GPiOs to control inputs (Buttons) and outputs (LEDs) using mqtt and homeassistant
- Configurable status leds for running and mqtt-status using RaspberryPi GPIOs
- RaspberryPi GPIO button support for restart and shutdown
  - Can be used to power down a RaspberryPi with a phyiscal button
- Cross-platform: Windows, Linux  (GPIOs only RaspberryPi)
- Configuration via YAML using web UI
- Various installation options, winget, pip, docker, remote script, windows setup, portable exe

---

## 🚀 Getting Started

The prgramm will be installed as a service placed in sytsem directories (details below).
After a succefull installation, the web ui can be opened using:

http://localhost:8100


### 🐧 Linux

Just use the install / uninstall script.
mqtt-presence will be installed as system.d service.

#### Install
```bash
curl -sSL "https://raw.githubusercontent.com/bjoernboeckle/mqtt-presence/main/scripts/install.sh" | bash
```

#### Uninstall
```bash
curl -sSL "https://raw.githubusercontent.com/bjoernboeckle/mqtt-presence/main/scripts/uninstall.sh" | bash -s -- --yes
```

---


### 🐳 Docker

Shutdown/Restart are not supported if running in a container and therefore they are disabled by default.

#### Docker compose
```yaml
services:
  mqtt-presence:
    image: bjoernboeckle/mqtt-presence:latest
    container_name: mqtt-presence
    volumes:
      - ./config/:/config
      - ./log/:/log
    network_mode: host      
```

---

### 🖥️ Windows

Download  and run the installer exe from the latest release:

[GitHub releases](https://github.com/bjoernboeckle/mqtt-presence/releases)

```bash
mqtt-presence-vx.x.x-setup.exe
```

Or use winget (latest version will be installed automatically)

```bash
winget install mqtt-presence
```

> **Note:** Installation and uninstallation require admin rights.


#### 📦  Or using portable Executable

Download the latest executable from the [GitHub releases](https://github.com/bjoernboeckle/mqtt-presence/releases) page.

```bash
mqtt-presence-vx.x.x.exe
```


---


### 🐍 As Python Package

Install via pip:

```bash
pip install mqtt-presence
```

Run:

```bash
mqtt-presence
```

Run as Python module:

```bash
python -m mqtt_presence.main
```

---



## ⚙️ Command Line Options

```bash
mqtt-presence.exe --config CONFIG_PATH --log LOG_PATH   # use CONFIG_PATH as configuration directory
                                                        # use LOG_PATH as log directory
```

---


# 📟 Web UI

Access the Web UI in your browser at:

```
http://<ip-address>:8100
```

Example: [http://localhost:8100](http://localhost:8100)


Apply configuration needs to executed to apply changed settings!

## App config

On this page app base settings can be changed:


<img src="docs/images/mqtt-presence-webui.png" alt="mqtt_presence Web UI screenshot" width="800">


| Parameter     | Description                                                                            |
|---------------|----------------------------------------------------------------------------------------|
| **Host**      | Web UI listen server 0.0.0.0 to listen on all IP adresses.                             |
| **Port**      | WebUI port number                                                                      |
| **update rate**  | Frequency which is used to update data and publishes to mqtt                        |
| **Enable MQTT**  | Enables / Disabled mqtt, if diabled, GPIOs etc.can still be used in WebUI           |
| **Enable PC Utilities**  | PC Information will not be send if dsabled                                  |
| **Enable RaspberryPi**  | Disabled RaspberryPi GPIOs                                                   |



## MQTT

This pages is used to configure mqtt connection and settings.

<img src="docs/images/mqtt-presence-webui-mqtt.png" alt="mqtt_presence Web UI screenshot" width="800">


| Parameter     | Description                                                                            |
|---------------|----------------------------------------------------------------------------------------|
| **Broker**    | IP address of mqtt broker                                                              |
| **Username**  | Username for mqtt broker                                                               |
| **Password**  | Password for mqtt user, password will not be save inside the configuration.yaml file   |
| **Prefix**    | Topic prefix for this client PC                                                        |
| **Enable Homeasistant<br>Discovery** | used to enable/disable home assitant discovery.<br>Homeassiatnat must have autodiscovery enabled.
| **Discovery Prefix**  | Discoveryprefix for homeassistant, should be "homeassistant" if bnot changed in HAS |
| **Device name**  | Device name shown in Homeassistant                                                       |


## PC utilities

This pages is used to enable/disable shutdown/resatrt commands and to view current oc status.

<img src="docs/images/mqtt-presence-webui-pc-utils.png" alt="mqtt_presence Web UI screenshot" width="800">


| Parameter     | Description                                                                            |
|---------------|----------------------------------------------------------------------------------------|
| **Enable shutdown**  | Shutdown command is is enabled/disabled                                         |
| **Enable reboot**    | Reboot command is is enabled/disabled                                           |
| **Enable infos**     | PC infos can be disabled (CPU frequency, ram usage ....                         |



## Raspberry PI

This interface allows you to add, edit, and remove GPIO pins for your Raspberry Pi in the app. Each GPIO pin can be configured either as an LED or a Button, with various setting options.

Each GPIO entry is displayed as a row.

On the far left is a red ❌ button to remove that GPIO entry.
To the right are all the input fields for configuring the GPIO.

<img src="docs/images/mqtt-presence-webui-raspberrypi.png" alt="mqtt_presence Web UI screenshot" width="800">


| Parameter     | Description                                                                            |
|---------------|----------------------------------------------------------------------------------------|
| **Pin**       | Numeric GPIO pin number on the Raspberry Pi. Example: 17. --> must be unique.          |
| **Mode**      | GPio is used as **LED** or **Button** (Input or output)                                |
| **Name**      | A free-text name to easily identify the pin.                                           |
|  **LED**                                                                                               |
| **LED Mode**  | **On/Off** or **Blink**, Blink toggles on off in 1 second intervalls if switched on    |
| **LED Function**  | **None**: LED / output can be used by mqtt or web interface <br> **App running**: LED is on while the app is running <br> **MQTT online**: The LED is on as long as there is an active mqtt connection  |
|  **Button**                                                                                             |
| **Bounce**    | Sets a debounce time, to avoid bouncing if a buton is pressed                           |
| **Pull-up**   | Enables/Disables an internal pull up resistor                                           |
| **Pressed**<br>**Released**<br>**Held**   | Sets a button function for pressed, released or held:<br>**None**: The button can be used for instance in homeassistant<br>**Shutdown** Shutsdown the PC<br>**Reboot** Reboots the pc                               |



---

## 🛠 Configuration

Configuration files are created on first run.

### Application Settings: (`configuration.yaml`)

This file is configured using the webUI.

```yaml
# Configuration file for MQTT Presence
# Please refer to the documentation for details on how to configure.
app:
  updateRate: 2
  webServer:
    host: 0.0.0.0
    port: 8100
  mqtt:
    enabled: true
    broker:
```

Changes require a restart of the service, which will be automatically done using the web UI.
Manuall changes require a manual restart.




## 📁 Directory Structure

### Installation paths used by installer/scripts:

| OS        | Paths                                                                                  |
|-----------|----------------------------------------------------------------------------------------|
| **Linux** | Install: `/opt/mqtt_presence` <br> Data: `/etc/mqtt_presence` <br> Logs: `/var/log`    |
| **Windows** | Install: `%ProgramData%\mqtt_presence` <br> Data: `%ProgramData%\mqtt_presence\data` <br> Logs: `%ProgramData%\mqtt_presence\log` |

---

### Default Config/Data Paths

| OS        | Config Path                                 |
|-----------|---------------------------------------------|
| Linux     | `~/.config/mqtt_presence`       |
| Windows   | `%APPDATA%\mqtt_presence`       |
| macOS     | `~/Library/Application Support/mqtt_presence` |

---

### Default Log Paths

| OS        | Log Path                                   |
|-----------|---------------------------------------------|
| Linux     | `~/.local/state/mqtt_presence/`      |
| Windows   | `%LOCALAPPDATA%\mqtt_presence\` |
| macOS     | `~/Library/Logs/mqtt_presence/`      |

---

### Cache Paths

| OS        | Cache Path                                |
|-----------|--------------------------------------------|
| Linux     | `~/.cache/mqtt_presence/status.cache`      |
| Windows   | `%LOCALAPPDATA%\mqtt_presence\Cache\status.cache` |
| macOS     | `~/Library/Caches/mqtt_presence/status.cache` |



---

## 🧠 License

Licensed under the Apache License 2.0.

