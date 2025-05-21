from enum import Enum
from typing import List

from dataclasses import dataclass, field

class GpioMode(Enum):
    NONE = -1
    INPUT = 0
    OUTPUT = 1
    LED = 2
    BUTTON = 3


@dataclass
class GpioButton:
    bounce_s: int = 0.1
    pull_up: bool = True


@dataclass
class Gpio:
    mode: GpioMode = GpioMode.NONE
    number: int = -1
    friendly_name: str = ""
    button: GpioButton = None


@dataclass
class RaspberryPiSettings:
    enable_raspberrypi = False
    simulated = None
    gpios: List[Gpio] = field(default_factory=list)
