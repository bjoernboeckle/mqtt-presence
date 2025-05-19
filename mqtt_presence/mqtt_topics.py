

from functools import partial
from dataclasses import dataclass
import psutil

from mqtt_presence.utils import Tools

def test(time1):
    print("Test received %s", time1)



# Sensor-Methoden
def _get_cpu_freq():
    freq = psutil.cpu_freq()
    if freq:
        return round(freq.current, 1)  # in MHz
    return None

def _get_memory_usage_percent():
    return psutil.virtual_memory().percent


def _get_cpu_load_1min():
    # 1-Minuten Load Average (nur auf Unix-Systemen sinnvoll, Windows gibt evtl. Fehler)
    try:
        return psutil.getloadavg()[0]
    except (AttributeError, OSError):
        # Fallback auf CPU-Auslastung der letzten Sekunde
        return psutil.cpu_percent(interval=1)

def _get_disk_usage_root_percent():
    return psutil.disk_usage('/').percent

def _get_disk_free_root_gb():
    free_bytes = psutil.disk_usage('/').free
    return round(free_bytes / (1024**3), 2)

def _get_net_bytes_sent():
    return psutil.net_io_counters().bytes_sent

def _get_net_bytes_recv():
    return psutil.net_io_counters().bytes_recv

def _get_cpu_temp_psutil():
    try:
        temps = psutil.sensors_temperatures()
        if not temps:
            return None
        for name, entries in temps.items():
            for entry in entries:
                if entry.label in ("Package id 0", "", None):
                    return entry.current
    except AttributeError:
        return None




@dataclass
class MqttSensorStateData:
    cpu_freq: str = None
    memory_usage: str = None
    cpu_load: str = None
    disk_usage_root: str = None
    disk_free_root: str = None
    net_bytes_sent: str = None
    net_bytes_recv: str = None
    cpu_temp: str = None

    def __getitem__(self, key):
        return getattr(self, key)
    
    def __setitem__(self, key, value):
        setattr(self, key, value)

@dataclass
class MqttBinarySensorData:
    status: str = None

    def __getitem__(self, key):
        return getattr(self, key)
    
    def __setitem__(self, key, value):
        setattr(self, key, value)


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
        self.sensors_data.cpu_freq = _get_cpu_freq()
        self.sensors_data.memory_usage = _get_memory_usage_percent()
        self.sensors_data.cpu_load = _get_memory_usage_percent()
        self.sensors_data.disk_usage_root = _get_disk_usage_root_percent()
        self.sensors_data.disk_free_root = _get_disk_free_root_gb()
        self.sensors_data.net_bytes_sent = _get_net_bytes_sent()
        self.sensors_data.net_bytes_recv = _get_net_bytes_recv()
        self.sensors_data.cpu_temp = _get_cpu_temp_psutil()


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