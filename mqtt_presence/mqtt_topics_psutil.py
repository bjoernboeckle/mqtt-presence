
import psutil

from mqtt_topics_data import MqttSensorStateData


class MqttTopics_PsUtil():

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
            for name, entries in temps.items():
                for entry in entries:
                    if entry.label in ("Package id 0", "", None):
                        return entry.current
        except AttributeError:
            return None


    staticmethod
    def update_sensors_data(sensors_data: MqttSensorStateData):
        sensors_data.cpu_freq = MqttTopics_PsUtil._get_cpu_freq()
        sensors_data.memory_usage = MqttTopics_PsUtil._get_memory_usage_percent()
        sensors_data.cpu_load = MqttTopics_PsUtil._get_memory_usage_percent()
        sensors_data.disk_usage_root = MqttTopics_PsUtil._get_disk_usage_root_percent()
        sensors_data.disk_free_root = MqttTopics_PsUtil._get_disk_free_root_gb()
        sensors_data.net_bytes_sent = MqttTopics_PsUtil._get_net_bytes_sent()
        sensors_data.net_bytes_recv = MqttTopics_PsUtil._get_net_bytes_recv()
        sensors_data.cpu_temp = MqttTopics_PsUtil._get_cpu_temp_psutil()        