import logging
import psutil


from mqtt_presence.mqtt.mqtt_data import MqttTopics, MqttTopic


logger = logging.getLogger(__name__)



# MQTT binary_sensors
__binary_sensors__ = {

}
# MQTT sensors
__sensors__ = {
    "cpu_freq": MqttTopic("CPU Frequency", unit = "MHz", icon = "sine-wave"),
    "memory_usage": MqttTopic("RAM Usage", unit = "%", icon = "memory"),
    "cpu_load": MqttTopic("CPU Load (1 min avg)", unit = "%", icon = "gauge"),
    "disk_usage_root": MqttTopic("Disk Usage", unit = "%", icon = "harddisk"),
    "disk_free_root": MqttTopic("Disk Free Space", unit = "GB", icon = "harddisk"),
    "net_bytes_sent": MqttTopic("Network Bytes Sent", unit = "B", icon = "network"),
    "net_bytes_recv": MqttTopic("Network Bytes Received", unit = "B", icon = "network"),
    "cpu_temp": MqttTopic("CPU Temperature", unit = "°C", icon = "thermometer")
}
# MQTT buttons
__buttons__ = {
    #"test": MqttTopic("Teste etwas", partial(test, 100)),
}


class PsUtil:
    def __init__(self):
        pass


    def exit(self):
        pass


    def init(self, _topic_action_callback):
        pass


    def create_topics(self, mqtt_topics: MqttTopics, prefix):
        #mqtt_topics.binary_sensors.update()
        mqtt_topics.sensors.update(__sensors__)
        #mqtt_topics.buttons.update(__buttons__)


    def update_data(self, mqtt_topics: MqttTopics):
        mqtt_topics.data["cpu_freq"] = self._get_cpu_freq()
        mqtt_topics.data["memory_usage"] = self._get_memory_usage_percent()
        mqtt_topics.data["cpu_load"] = self._get_memory_usage_percent()
        mqtt_topics.data["disk_usage_root"] = self._get_disk_usage_root_percent()
        mqtt_topics.data["disk_free_root"] = self._get_disk_free_root_gb()
        mqtt_topics.data["net_bytes_sent"] = self._get_net_bytes_sent()
        mqtt_topics.data["net_bytes_recv"] = self._get_net_bytes_recv()
        mqtt_topics.data["cpu_temp"] = self._get_cpu_temp_psutil()
        


    def _get_cpu_freq(self):
        freq = psutil.cpu_freq()
        if freq:
            return round(freq.current, 1)  # in MHz
        return None

    def _get_memory_usage_percent(self):
        return psutil.virtual_memory().percent

    
    def _get_cpu_load_1min(self):
        # 1-Minuten Load Average (nur auf Unix-Systemen sinnvoll, Windows gibt evtl. Fehler)
        try:
            return psutil.getloadavg()[0]
        except (AttributeError, OSError):
            # Fallback auf CPU-Auslastung der letzten Sekunde
            return psutil.cpu_percent(interval=1)

    
    def _get_disk_usage_root_percent(self):
        return psutil.disk_usage('/').percent

    
    def _get_disk_free_root_gb(self):
        free_bytes = psutil.disk_usage('/').free
        return round(free_bytes / (1024**3), 2)

    
    def _get_net_bytes_sent(self):
        return psutil.net_io_counters().bytes_sent

    
    def _get_net_bytes_recv(self):
        return psutil.net_io_counters().bytes_recv

    
    def _get_cpu_temp_psutil(self):
        try:
            temps = psutil.sensors_temperatures()
            if not temps:
                return None
            for _, entries in temps.items():
                for entry in entries:
                    if entry.label in ("Package id 0", "", None):
                        return entry.current
        except AttributeError:
            return None
        return None


