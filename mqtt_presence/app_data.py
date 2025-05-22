from dataclasses import dataclass, field

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
