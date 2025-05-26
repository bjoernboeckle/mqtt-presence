
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from mqtt_presence.devices.device_data import DeviceSettings

class GpioMode(Enum):
    LED = "led"
    BUTTON = "button"

class GpioButton_Function(Enum):
    SHUTDOWN = "shutdown"
    REBOOT = "reboot"


@dataclass
class GpioButton:
    bounce_s: float = 0.1
    pull_up: bool = True
    function_pressed:GpioButton_Function = None
    function_released:GpioButton_Function = None
    function_held:GpioButton_Function = None



@dataclass
class Gpio:
    mode: GpioMode = GpioMode.LED
    number: int = 0
    friendly_name: str = ""
    button: Optional[GpioButton] = None



@dataclass
class RaspberryPiSettings(DeviceSettings):
    gpios: List[Gpio] = field(default_factory=list)


    @staticmethod
    def get_default_raspberrypi_settings() -> 'RaspberryPiSettings':
        return RaspberryPiSettings(
            enabled=True,
            gpios=[
                Gpio(mode=GpioMode.LED, number=19, friendly_name="Red"),
                Gpio(mode=GpioMode.LED, number=21, friendly_name="Blue"),
                Gpio(mode=GpioMode.BUTTON, number=16, friendly_name="Powerdown")
                     #,button=GpioButton(function_held=GpioButton_Function.SHUTDOWN))
            ]
        )
