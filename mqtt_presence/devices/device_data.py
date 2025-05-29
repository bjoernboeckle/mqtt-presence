from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List
from functools import partial

class HomeassistantType(Enum):
    BINARY_SENSOR = "binary_sensor"
    SENSOR = "sensor"
    BUTTON = "button"
    SWITCH = "switch"
    DEVICE_AUTOMATION = "device_automation"


@dataclass
class Homeassistant:
    type: HomeassistantType = HomeassistantType.BINARY_SENSOR
    icon: str = None
    actions: List[str] = None


@dataclass
class DeviceData:
    friendly_name: str
    unit: Optional[str] = None
    action: Optional[partial] = field(default=None, repr=False, compare=False)
    data: Optional[str] = None
    homeassistant: Optional[Homeassistant] = None



@dataclass
class DeviceSettings:
    enabled: bool = True
