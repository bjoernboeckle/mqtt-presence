from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List
from functools import partial

class DeviceType(Enum):
    BINARY_SENSOR = "binary_sensor"
    SENSOR = "sensor"
    BUTTON = "button"
    SWITCH = "switch"
    DEVICE_AUTOMATION = "device_automation"




@dataclass
class DeviceData:
    friendly_name: str
    unit: Optional[str] = None
    action: Optional[partial] = field(default=None, repr=False, compare=False)
    data: Optional[str] = None
    icon: Optional[str] = None
    type: Optional[DeviceType] = DeviceType.BINARY_SENSOR
    actions: Optional[List[str]] = None


@dataclass
class DeviceSettings:
    enabled: bool = True
