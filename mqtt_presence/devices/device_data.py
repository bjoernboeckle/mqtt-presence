from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List
from functools import partial



class DeviceKey(str, Enum):
    PC_UTILS = "pc_utils"
    RASPBERRY_PI = "raspberrypi"
    MOUSE_JIGGLER = "mouse_jiggler"




class DeviceType(str, Enum):
    BINARY_SENSOR = "binary_sensor"
    SENSOR = "sensor"
    BUTTON = "button"
    SWITCH = "switch"
    SELECT = "select"
    DEVICE_AUTOMATION = "device_automation"



@dataclass
class DeviceData:
    friendly_name: str
    unit: Optional[str] = None
    data: Optional[str] = None
    icon: Optional[str] = None
    type: Optional[DeviceType] = DeviceType.BINARY_SENSOR
    actions: Optional[List[str]] = None
    options: Optional[List[str]] = None


@dataclass
class DeviceSettings:
    enabled: bool = True
