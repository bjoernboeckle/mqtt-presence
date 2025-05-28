
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

class GpioLed_Function(Enum):
    RUNNING = "running"
    MQTT_ONLINE = "mqtt-online"

class GpioLed_Mode(Enum):
    ON_OFF = "on-off"
    BLINK = "blink"


@dataclass
class GpioButton:
    bounce_s: float = 0.1
    pull_up: bool = True
    function_pressed:Optional[GpioButton_Function] = None
    function_released:Optional[GpioButton_Function] = None
    function_held:Optional[GpioButton_Function] = None


@dataclass
class GpioLed:
    led_mode: GpioLed_Mode = GpioLed_Mode.ON_OFF
    led_function: Optional[GpioLed_Function] = None


@dataclass
class Gpio:
    mode: GpioMode = GpioMode.LED
    number: int = 0
    friendly_name: str = ""
    button: Optional[GpioButton] = None
    led: Optional[GpioLed] = None



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
