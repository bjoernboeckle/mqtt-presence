
from mqtt_presence.devices.raspberrypi.raspberrypi_device import RaspberryPiDevice
from mqtt_presence.devices.psutil.psutil import PsUtil
from mqtt_presence.utils import Tools
from mqtt_presence.mqtt.mqtt_data import MqttTopics, MqttTopic


def test(_payload):
    print("TESSSSSTTTTTTTTTTTTTTT")

# MQTT buttons
__buttons__ = {
    "shutdown": MqttTopic("Shutdown pc", action = Tools.shutdown),
    "reboot": MqttTopic("Reboot pc", action = Tools.reboot),
    #"test": MqttTopic("Teste etwas", partial(test, 100)),
    "test": MqttTopic("Teste etwas", test),
}


class Devices:
    def __init__(self):    
            self.devices = [ RaspberryPiDevice(), PsUtil()]


    def init(self, topic_callback):
        for device in self.devices:
            device.init(topic_callback)

    def exit(self):
        for device in self.devices:
            device.exit()

    def create_topics(self, mqtt_topics, prefix):
        mqtt_topics.buttons.update(__buttons__)
        for device in self.devices:
            device.create_topics(mqtt_topics, prefix)


    def update_data(self, mqtt_topics: MqttTopics):
        for device in self.devices:
            device.update_data(mqtt_topics)
