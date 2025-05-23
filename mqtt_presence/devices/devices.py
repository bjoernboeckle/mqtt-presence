import logging
from functools import partial

from mqtt_presence.devices.raspberrypi.raspberrypi_device import RaspberryPiDevice
from mqtt_presence.devices.psutil.psutil import PsUtil
from mqtt_presence.utils import Tools
from mqtt_presence.mqtt.mqtt_data import MqttTopic, MQTTHomeassistant, MQTTHomeassistantType

logger = logging.getLogger(__name__)





class Devices:
    def __init__(self, config_path: str):    
            self.devices = [ RaspberryPiDevice(config_path), PsUtil(config_path)]
            self.data: dict[str, str] = {}


    def init(self, topic_callback):
        for device in self.devices:
            device.init(topic_callback)


    def exit(self):
        for device in self.devices:
            device.exit()


    def create_topics(self) -> dict[str, MqttTopic]:
        topics: dict[str, MqttTopic] = {}
        # MQTT buttons
        device_buttons = {
            "shutdown": MqttTopic( "Shutdown pc", action = partial(self._device_command, "shutdown"), homeassistant=MQTTHomeassistant(MQTTHomeassistantType.BUTTON)),
            "reboot": MqttTopic("Reboot pc", action = partial(self._device_command, "reboot"), homeassistant=MQTTHomeassistant(MQTTHomeassistantType.BUTTON)),
            "test": MqttTopic("Teste button", action = partial(self._device_command, "test"), homeassistant=MQTTHomeassistant(MQTTHomeassistantType.BUTTON)),
        }
        topics.update(device_buttons)
        for device in self.devices:
            topics.update(device.create_topics())

        return topics


    def update_data(self):
        for device in self.devices:
            device.update_data(self.data)


    def _device_command(self, function, payload):
        logger.info("✏️  Device command: %s", payload)
        if ( function == "shutdown"): Tools.shutdown()
        elif ( function == "reboot"): Tools.reboot()
        elif ( function == "test"): logger.info("🧪 Test command")
        else: logger.warning("⚠️  Unknown Device command: %s", payload)
