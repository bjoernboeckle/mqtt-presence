from dataclasses import dataclass, field

from mqtt_presence.utils import Tools

SECRET_KEY_FILE = "secret.key"
CONFIG_DATA_FILE = "config.json"
CONFIG_YAML_FILE = "config.yaml"


@dataclass
class ConfigFiles:
    secret_file: str = Tools.get_config_path(Tools.APP_NAME, SECRET_KEY_FILE)
    config_file: str = Tools.get_config_path(Tools.APP_NAME,CONFIG_DATA_FILE)
    yaml_file: str = Tools.get_config_path(Tools.APP_NAME,CONFIG_YAML_FILE)



@dataclass
class Broker:
    host: str = "localhost"
    port: int = 1883
    username: str = "mqttuser"
    encrypted_password: str = ""
    keepalive: int = 30
    prefix: str = ""


@dataclass
class Homeassistant:
    enabled: bool = True
    discovery_prefix: str = "homeassistant"
    device_name: str = ""


@dataclass
class Mqtt:
    broker: Broker = field(default_factory=Broker)
    homeassistant: Homeassistant = field(default_factory=Homeassistant)

@dataclass
class Configuration:
    mqtt: Mqtt = field(default_factory=Mqtt)
