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

Start
Run:

    mqtt-presence 

or using console ui (testing purposes)

    mqtt-presence --ui console

Or use python module:

    python -m mqtt_presence.main


### As binary
Download and run executable created by Installer

    mqtt-presence
    mqtt-presence.exe




### Start Container
TODO: Image not yet published.

        docker-compose up -d

        docker run -d -p 5000:5000 --name mqtt_presence mqtt_presence
        
        If  GPIO is required  (only  Raspberry Pi):
        docker run --privileged -d -p 5000:5000 --name mqtt_presence mqtt_presence


## Configuration

Configuration and application data is created at first startup and placed in directory: "config".

### Application configuration options (config.yaml):
    
    app:
    disableShutdown: false
    mqtt:
        client_id: mqtt-presence_PCName
    webServer:
        host: 0.0.0.0
        port: 8000

After changeing parameters, the app need to be restarted.


### Application data (config.json)

Application data can be modified using the web ui. After saving new values the new settings are applied immedeiatly.
Existing config.json will be overwritten, so manual editing is not recommended.



# Create deployments


## Installer

    pyinstaller --onefile --name mqtt-presence mqtt_presence/main.py
    python -m PyInstaller --onefile --name mqtt-presence mqtt_presence/main.py



## Packet
    python -m build
    twine upload dist/*


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

