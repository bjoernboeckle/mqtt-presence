from dataclasses import dataclass, field
from typing import List
from enum import Enum

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




class GpioMode(Enum):
    NONE = -1
    INPUT = 0
    OUTPUT = 1
    LED = 2
    BUTTON = 3


@dataclass
class Gpio:
    mode: GpioMode = GpioMode.NONE 
    number: int = -1
    friendly_name = ""

@dataclass 
class RaspberryPiSettings:
    enable_raspberrypi = False
    gpios: List[Gpio] = field(default_factory=list)


@dataclass
class Configuration:
    mqtt: Mqtt = field(default_factory=Mqtt)
    raspberry_pi = field(default_factory=RaspberryPiSettings)

