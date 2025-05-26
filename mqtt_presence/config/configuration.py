from dataclasses import dataclass, field



from mqtt_presence.devices.raspberrypi.raspberrypi_data import RaspberryPiSettings
from mqtt_presence.devices.pc_utils.pc_utils_data import PcUtilsSettings

########################Webserver##############

@dataclass
class WebServerAppConfig:
    host: str = "0.0.0.0"
    port: int = 8100

######################## MQTT ##############

@dataclass
class Broker:
    client_id: str = "" # MQTT broker configuration
    host: str = "localhost"
    port: int = 1883
    username: str = "mqttuser"
    keepalive: int = 30
    prefix: str = ""


@dataclass
class Homeassistant:
    enabled: bool = True  # Enable Home Assistant discovery
    discovery_prefix: str = "homeassistant"
    device_name: str = ""
    enableAutoCleanup: bool = True


@dataclass
class Mqtt:
    broker: Broker = field(default_factory=Broker)
    homeassistant: Homeassistant = field(default_factory=Homeassistant)



@dataclass
class Devices:
    raspberryPi: RaspberryPiSettings = field(default_factory=RaspberryPiSettings)
    pc_utils: PcUtilsSettings = field(default_factory=PcUtilsSettings)





@dataclass
class Configuration:
    updateRate: int = 5  # Update interval in seconds
    webServer: WebServerAppConfig = field(default_factory=WebServerAppConfig)    # pylint: disable=invalid-name
    mqtt: Mqtt = field(default_factory=Mqtt)
    devices: Devices = field(default_factory=Devices)
