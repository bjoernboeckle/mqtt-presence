import logging
from functools import partial

from mqtt_presence.devices.raspberrypi.raspberrypi_device import RaspberryPiDevice
from mqtt_presence.devices.psutil.psutil import PsUtil
from mqtt_presence.utils import Tools
from mqtt_presence.mqtt.mqtt_data import MqttTopics, MqttTopic

logger = logging.getLogger(__name__)


class Devices:
    def __init__(self, config_path: str):    
            self.devices = [ RaspberryPiDevice(config_path), PsUtil(config_path)]


    def init(self, topic_callback):
        for device in self.devices:
            device.init(topic_callback)

    def exit(self):
        for device in self.devices:
            device.exit()

    def create_topics(self, mqtt_topics):
        # MQTT buttons
        device_buttons = {
            "shutdown": MqttTopic("Shutdown pc", action = partial(self._devcie_command, "shutdown")),
            "reboot": MqttTopic("Reboot pc", action = partial(self._devcie_command, "reboot")),
            #"test": MqttTopic("Teste button", action = partial(self._devcie_command, "test")),
        }

        mqtt_topics.buttons.update(device_buttons)
        for device in self.devices:
            device.create_topics(mqtt_topics)


    def update_data(self, mqtt_topics: MqttTopics):
        for device in self.devices:
            device.update_data(mqtt_topics)

    
    def _devcie_command(self, function, payload):
        logger.info("✏️  Device command: %s", payload)
        if ( function == "shutdown"): Tools.shutdown()
        elif ( function == "reboot"): Tools.reboot()
        #elif ( function == "test"): logger.info("🧪 Test command")
        else: logger.warning("⚠️  Unknown Device command: %s", payload)
