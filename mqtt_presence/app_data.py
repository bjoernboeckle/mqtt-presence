from dataclasses import dataclass, field

SECRET_KEY_FILE = "config/secret.key"
CONFIG_DATA_FILE = "config/config.json"
CONFIG_YAML_FILE = "config/config.yaml"


@dataclass
class ConfigFiles:
    secretFile: str = SECRET_KEY_FILE
    configFile: str = CONFIG_DATA_FILE
    yamlFile: str = CONFIG_YAML_FILE



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


