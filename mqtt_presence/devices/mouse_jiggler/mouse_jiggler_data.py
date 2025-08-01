from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from mqtt_presence.devices.device_data import DeviceSettings


class jigglerMode(Enum):
    STOPPED = "stopped"
    ENABLED = "enabled"


@dataclass
class MouseJigglerSettings(DeviceSettings):
    serial_port: str = "COM1"
    jigglerMode: bool = False
