import logging
import psutil

from functools import partial

from mqtt_presence.mqtt.mqtt_data import MqttTopic, MQTTHomeassistant, MQTTHomeassistantType
from mqtt_presence.config.configuration import Configuration
from mqtt_presence.utils import Tools
from mqtt_presence.devices.pc_utils.pc_utils_data import PcUtilsSettings

logger = logging.getLogger(__name__)


class PcUtils:
    def __init__(self):
        pass


    def exit(self):
        pass


    def init(self, config: Configuration, _topic_callback):
        self.settings: PcUtilsSettings = config.devices.pc_utils



    def create_topics(self) -> dict[str, MqttTopic]:
        topics: dict[str, MqttTopic] = {
            # MQTT buttons
            "test": MqttTopic("Teste button", action = partial(self._device_command, "test"), homeassistant=MQTTHomeassistant(MQTTHomeassistantType.BUTTON)),
            # MQTT sensors
            "cpu_freq": MqttTopic("CPU Frequency", homeassistant=MQTTHomeassistant(type=MQTTHomeassistantType.SENSOR, unit = "MHz", icon = "sine-wave")),
            "memory_usage": MqttTopic("RAM Usage", homeassistant=MQTTHomeassistant(type=MQTTHomeassistantType.SENSOR, unit = "%", icon = "memory" )),
            "cpu_load": MqttTopic("CPU Load (1 min avg)", homeassistant=MQTTHomeassistant(type=MQTTHomeassistantType.SENSOR, unit = "%", icon = "gauge" )),
            "disk_usage_root": MqttTopic("Disk Usage", homeassistant=MQTTHomeassistant(type=MQTTHomeassistantType.SENSOR, unit = "%", icon = "harddisk")),
            "disk_free_root": MqttTopic("Disk Free Space", homeassistant=MQTTHomeassistant(type=MQTTHomeassistantType.SENSOR, unit = "GB", icon = "harddisk" )),
            "net_bytes_sent": MqttTopic("Network Bytes Sent", homeassistant=MQTTHomeassistant(type=MQTTHomeassistantType.SENSOR, unit = "B", icon = "network" )),
            "net_bytes_recv": MqttTopic("Network Bytes Received", homeassistant=MQTTHomeassistant(type=MQTTHomeassistantType.SENSOR, unit = "B", icon = "network" )),
            "cpu_temp": MqttTopic("CPU Temperature", homeassistant=MQTTHomeassistant(type=MQTTHomeassistantType.SENSOR, unit = "°C", icon = "thermometer" ))
        }
        if self.settings.enableShutdown:
            topics["shutdown"] = MqttTopic("Shutdown PC", action=partial(self._device_command, "shutdown"), homeassistant=MQTTHomeassistant(MQTTHomeassistantType.BUTTON))
        if self.settings.enableReboot:
            topics["reboot"] = MqttTopic("Reboot PC", action=partial(self._device_command, "reboot"), homeassistant=MQTTHomeassistant(MQTTHomeassistantType.BUTTON))
        
        return topics


    def update_data(self, device_data: dict[str, str]):
        device_data["cpu_freq"] = self._get_cpu_freq()
        device_data["memory_usage"] = self._get_memory_usage_percent()
        device_data["cpu_load"] = self._get_memory_usage_percent()
        device_data["disk_usage_root"] = self._get_disk_usage_root_percent()
        device_data["disk_free_root"] = self._get_disk_free_root_gb()
        device_data["net_bytes_sent"] = self._get_net_bytes_sent()
        device_data["net_bytes_recv"] = self._get_net_bytes_recv()
        device_data["cpu_temp"] = self._get_cpu_temp_psutil()



    def _device_command(self, function, payload):
        logger.info("✏️  Device command: %s", payload)
        if ( function == "shutdown"): Tools.shutdown()
        elif ( function == "reboot"): Tools.reboot()
        elif ( function == "test"): logger.info("🧪 Test command")
        else: logger.warning("⚠️  Unknown Device command: %s", payload)


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
