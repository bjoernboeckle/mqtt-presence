from dataclasses import dataclass

# pylint: disable=R0902
# pylint: enable=R0902



@dataclass
class MqttTopic:
    def __init__(self, friendly_name, action = None, unit = None, icon = None, subtype = None):
        self.friendly_name = friendly_name
        self.action = action
        self.unit = unit
        self.icon = icon
        self.subtype = subtype


@dataclass 
class MqttTopics:
    def __init__(self, mqtt_app):
        self.binary_sensors: dict[str, MqttTopic] = {}
        self.sensors: dict[str, MqttTopic] = {}
        self.buttons: dict[str, MqttTopic] = {}
        self.switches: dict[str, MqttTopic] = {}
        self.device_automations: dict[str, MqttTopic] = {}

        self.data: dict[str, MqttTopic] = {}
        self.data_old: dict[str, MqttTopic] = {}
  


    def get_topics_by_group(self):
        return {
            "binary_sensor": self.binary_sensors,
            "sensor": self.sensors,
            "button": self.buttons,
            "switch": self.switches,
            "device_automation": self.device_automations,
        }
