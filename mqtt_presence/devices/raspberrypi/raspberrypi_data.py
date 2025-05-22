from enum import Enum
from typing import List
import yaml
from dataclasses import dataclass, field, is_dataclass, asdict


class GpioMode(Enum):
    LED = 0
    BUTTON = 1

class GpioButton_Function(Enum):
    SHUTDOWN = 0
    REBOOT = 1


@dataclass
class GpioButton:
    bounce_s: int = 0.1
    pull_up: bool = True
    function_pressed:GpioButton_Function = None
    function_released:GpioButton_Function = None
    function_held:GpioButton_Function = None



@dataclass
class Gpio:
    mode: GpioMode = None
    number: int = None
    friendly_name: str = ""
    button: GpioButton = None



@dataclass
class RaspberryPiSettings:
    enable_raspberrypi: bool = False
    simulated: bool = None
    gpios: List[Gpio] = field(default_factory=list)
