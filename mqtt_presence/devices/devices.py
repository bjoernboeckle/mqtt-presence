import logging

from mqtt_presence.devices.raspberrypi.raspberrypi_device import RaspberryPiDevice
from mqtt_presence.devices.pc_utils.pc_utils import PcUtils
from mqtt_presence.mqtt.mqtt_data import MqttTopic
from mqtt_presence.config.configuration import Configuration

logger = logging.getLogger(__name__)


class Devices:
    def __init__(self):    
            self.devices: dict[str, object] = { "raspberry": RaspberryPiDevice(), "pcUtils": PcUtils() }
            self.data: dict[str, str] = {}


    def init(self, config: Configuration, topic_callback):
        for device in self.devices.values():
            device.init(config, topic_callback)


    def exit(self):
        for device in self.devices.values():
            device.exit()


    def create_topics(self) -> dict[str, MqttTopic]:
        topics: dict[str, MqttTopic] = {}
        for device in self.devices.values():
            topics.update(device.create_topics())

        return topics


    def update_data(self):
        for device in self.devices.values():
            device.update_data(self.data)


