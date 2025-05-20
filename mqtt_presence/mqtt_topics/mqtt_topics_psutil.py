
import psutil

from mqtt_presence.mqtt_topics.mqtt_topics_data import MqttSensorStateData


class MqttTopicsPsUtil():

    @staticmethod
    def _get_cpu_freq():
        freq = psutil.cpu_freq()
        if freq:
            return round(freq.current, 1)  # in MHz
        return None

    @staticmethod
    def _get_memory_usage_percent():
        return psutil.virtual_memory().percent

    @staticmethod
    def _get_cpu_load_1min():
        # 1-Minuten Load Average (nur auf Unix-Systemen sinnvoll, Windows gibt evtl. Fehler)
        try:
            return psutil.getloadavg()[0]
        except (AttributeError, OSError):
            # Fallback auf CPU-Auslastung der letzten Sekunde
            return psutil.cpu_percent(interval=1)

    @staticmethod
    def _get_disk_usage_root_percent():
        return psutil.disk_usage('/').percent

    @staticmethod
    def _get_disk_free_root_gb():
        free_bytes = psutil.disk_usage('/').free
        return round(free_bytes / (1024**3), 2)

    @staticmethod
    def _get_net_bytes_sent():
        return psutil.net_io_counters().bytes_sent

    @staticmethod
    def _get_net_bytes_recv():
        return psutil.net_io_counters().bytes_recv

    @staticmethod
    def _get_cpu_temp_psutil():
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


    @staticmethod
    def update_sensors_data(sensors_data: MqttSensorStateData):
        sensors_data.cpu_freq = MqttTopicsPsUtil._get_cpu_freq()
        sensors_data.memory_usage = MqttTopicsPsUtil._get_memory_usage_percent()
        sensors_data.cpu_load = MqttTopicsPsUtil._get_memory_usage_percent()
        sensors_data.disk_usage_root = MqttTopicsPsUtil._get_disk_usage_root_percent()
        sensors_data.disk_free_root = MqttTopicsPsUtil._get_disk_free_root_gb()
        sensors_data.net_bytes_sent = MqttTopicsPsUtil._get_net_bytes_sent()
        sensors_data.net_bytes_recv = MqttTopicsPsUtil._get_net_bytes_recv()
        sensors_data.cpu_temp = MqttTopicsPsUtil._get_cpu_temp_psutil()
