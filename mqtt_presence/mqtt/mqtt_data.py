from dataclasses import dataclass, field
from enum import Enum
from typing import List
# pylint: disable=R0902
# pylint: enable=R0902



class MQTTHomeassistantType(Enum):
    BINARY_SENSOR = "binary_sensor"
    SENSOR = "sensor"
    BUTTON = "button"
    SWITCH = "switch"
    DEVICE_AUTOMATION = "device_automation"


@dataclass    
class MQTTHomeassistant:
    type: MQTTHomeassistantType = MQTTHomeassistantType.BINARY_SENSOR
    unit: str = None
    icon: str = None
    actions: List[str] = None


@dataclass
class MqttTopic:
    def __init__(self, friendly_name, action = None, data = None, homeassistant: MQTTHomeassistant = None):
        self.friendly_name = friendly_name
        self.action = action
        self.data = data
        self.homeassistant = homeassistant
        

