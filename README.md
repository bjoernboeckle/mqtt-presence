# mqtt_presence

This application connects to an mqtt broker and publishes an online state.
This state can be used for instance by homeassitant to detect if a PC is stil running.

Additional a reboot and shutdown command are available, to reboot, shutdown the system via mqtt.
Both is only possible in case the app is running with sudo rights.

In case homeassistant is not requiered it can also be disabled.


## Start / Install


### As module in python:
Install:

    pip install mqtt-presence

Start/Run:

    mqtt-presence 

    # or using console ui (testing purposes) # 

    mqtt-presence --ui console

    # Or use python module: #

    python -m mqtt_presence.main


### As binary
Download and run executable created by Installer

    mqtt-presence.exe


### Command line parameters

    mqtt-presence.exe --ui webui      # Starts web ui (default)
    mqtt-presence.exe --ui console    # Use a console UI


### Start Container
TODO: Image not yet published.

        docker-compose up -d

        docker run -d -p 5000:5000 --name mqtt_presence mqtt_presence
        
        If  GPIO is required  (only  Raspberry Pi):
        docker run --privileged -d -p 5000:5000 --name mqtt_presence mqtt_presence



## Configuration

Configuration and application data is created at first startup and placed inside the config direcories.


### Application configuration options (config.yaml):
    
    app:
        disableShutdown: false            # true disables real shutdown/restart for testing purpeses
    mqtt:
        client_id: mqtt-presence_PCName   # mqtt client ID, should not be changed
    webServer:
        host: 0.0.0.0                     # host/port for web settings page
        port: 8000

After changeing parameters, the app need to be restarted.


### Application data (config.json)

Application data can be modified using the web ui. After saving new values the new settings are applied immedeiatly.
Existing config.json will be overwritten, so manual editing is not recommended.

## Directories

### Configuration files (config.yaml, config.json, secret,key)

| OS          | Place of configuration                                 | Examples                                                            |
| ----------- | ------------------------------------------------------ | ------------------------------------------------------------------- |
| **Windows** | `%APPDATA%\<App-Name>\config.yaml`                     | `C:\Users\User\AppData\Roaming\mqtt_presence\config.yaml`           |
| **Linux**   | `~/.config/<App-Name>/config.yaml`                     | `/home/user/.config/mqtt_presence/config.yaml`                      |
| **macOS**   | `~/Library/Application Support/<App-Name>/config.yaml` | `/Users/user/Library/Application Support/mqtt_presence/config.yaml` |




### Log file

Logs are placed depending on operating systems in log directory:

| OS             | Place of configuration            | Examples                                                      |
| -------------- | --------------------------------- | ------------------------------------------------------------- |
| **Windows**    | `%LOCALAPPDATA%\<App-Name>\Logs\` | `C:\Users\<User>\AppData\Local\mqtt_presence\Logs\app.log`    |
| **Linux**      | `$XDG_STATE_HOME/<app-name>/`     | `/home/user/.local/state/mqtt_presence/app.log`               |
| *(Fallback)*   | `$XDG_CACHE_HOME/log/<app-name>/` | `/home/user/.cache/log/mqtt_presence/app.log` *(if required)* |
| **macOS**      | `~/Library/Logs/<App-Name>/`      | `/Users/<User>/Library/Logs/mqtt_presence/app.log`            |




### Cache files

Temp files are placed depending operating system in cache:

| OS             | Place of configuration             | Examples                                                         |
| -------------- | ---------------------------------- | ---------------------------------------------------------------- |
| **Windows**    | `%LOCALAPPDATA%\<App-Name>\Cache\` | `C:\Users\<User>\AppData\Local\mqtt_presence\Cache\status.cache` |
| **Linux**      | `$XDG_CACHE_HOME/<app-name>/`      | `/home/user/.cache/mqtt_presence/status.cache`                   |
| **macOS**      | `~/Library/Caches/<App-Name>/`     | `/Users/<User>/Library/Caches/mqtt_presence/status.cache`        |




# Create deployments

## Package

    # build
    pip install --upgrade build
    python -m build

    #upload
    pip install --upgrade twine
    twine upload dist/*

## Exe Installer


    python -m PyInstaller mqtt-presence.spec

Without spec:

    pyinstaller --onefile --name mqtt-presence mqtt_presence/main.py
    python -m PyInstaller --onefile --name mqtt-presence mqtt_presence/main.py



## Container

TODO:

### Build container:
    docker compose build
    docker compose up --build


### Delete image/existing container
    docker container rm mqtt-presence
    docker image rm mqtt-presence


### Save/load image:
    docker save -o mqtt-presence.tar mqtt-presence
    docker load -i ./mqtt-presence.tar

