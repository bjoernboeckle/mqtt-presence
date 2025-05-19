from dataclasses import dataclass

from mqtt_presence.utils import Tools
from mqtt_presence.mqtt_topics_data import MqttBinarySensorData, MqttSensorStateData
from mqtt_presence.mqtt_topics_psutil import MqttTopics_PsUtil


def test(time1):
    print("Test received %s", time1)


@dataclass
class MqttTopic:
    def __init__(self, friendly_name, action = None, unit = None, icon = None):
        self.friendly_name = friendly_name
        self.action = action
        self.unit = unit
        self.icon = icon



# MQTT binary_sensors
__binary_sensors__ = {
    "status": MqttTopic("Online state", None),
}
# MQTT sensors
__sensors__ = {
    "cpu_freq": MqttTopic("CPU Frequency", unit = "MHz", icon = "sine-wave"),
    "memory_usage": MqttTopic("RAM Usage", unit = "%", icon = "memory"),
    "cpu_load": MqttTopic("CPU Load (1 min avg)", unit = "%"),
    "disk_usage_root": MqttTopic("Disk Usage", unit = "%", icon = "harddisk"),
    "disk_free_root": MqttTopic("Disk Free Space", unit = "GB", icon = "harddisk"),
    "net_bytes_sent": MqttTopic("Network Bytes Sent", unit = "B", icon = "network"),
    "net_bytes_recv": MqttTopic("Network Bytes Received", unit = "B", icon = "network"),
    "cpu_temp": MqttTopic("CPU Temperature", unit = "°C", icon = "thermometer")
}
# MQTT buttons
__buttons__ = {
    "shutdown": MqttTopic("Shutdown pc", action = Tools.shutdown),
    "reboot": MqttTopic("Reboot pc", action = Tools.reboot),
    #"test": MqttTopic("Teste etwas", partial(test, 100)),
}


class MqttTopics:
    def __init__(self):
        self.binary_sensors = __binary_sensors__
        self.sensors = __sensors__
        self.buttons = __buttons__

        self.binary_sensors_dats = MqttBinarySensorData()
        self.sensors_data = MqttSensorStateData()
        self.sensors_data_old = MqttSensorStateData()


    def _update_sensor_data(self):
        MqttTopics_PsUtil.update_sensors_data(self.sensors_data)


    def _update_binary_sensor_data(self):
        self.status = "online"


    def update_data(self):
        self._update_binary_sensor_data()
        self._update_sensor_data()

        
    def get_topics_by_group(self):
        return {
            "binary_sensor": self.binary_sensors,
            "sensor": self.sensors,
            "button": self.buttons
        }