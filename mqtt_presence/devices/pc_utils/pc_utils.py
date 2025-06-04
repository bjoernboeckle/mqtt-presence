import logging
import psutil

from functools import partial

from mqtt_presence.devices.device_data import DeviceData, DeviceType
from mqtt_presence.config.configuration import Configuration
from mqtt_presence.utils import Tools
from mqtt_presence.devices.pc_utils.pc_utils_data import PcUtilsSettings
from mqtt_presence.devices.device import Device


logger = logging.getLogger(__name__)


class PcUtils(Device):
    def __init__(self, device_key):
        super().__init__(device_key)

    def exit(self):
        pass


    def init(self, config: Configuration, _topic_callback):
        self.settings: PcUtilsSettings = config.devices.pc_utils
        self.data.clear()
        if not self.settings.enabled:
            return

        if self.settings.enableInfos:
            self.data.update( {
                # MQTT buttons
                "test": DeviceData("Test button", action = partial(self._device_command, "test"), type = DeviceType.BUTTON, icon="test-tube"),
                # MQTT sensors
                "cpu_freq": DeviceData("CPU Frequency", unit = "MHz", type = DeviceType.SENSOR, icon = "sine-wave"),
                "memory_usage": DeviceData("RAM Usage", unit = "%", type = DeviceType.SENSOR, icon = "memory" ),
                "cpu_load": DeviceData("CPU Load (1 min avg)", unit = "%", type = DeviceType.SENSOR, icon = "gauge" ),
                "disk_usage_root": DeviceData("Disk Usage", unit = "%", type = DeviceType.SENSOR, icon = "harddisk"),
                "disk_free_root": DeviceData("Disk Free Space", unit = "GB", type = DeviceType.SENSOR, icon = "harddisk" ),
                "net_bytes_sent": DeviceData("Network Bytes Sent", unit = "B", type = DeviceType.SENSOR, icon = "network" ),
                "net_bytes_recv": DeviceData("Network Bytes Received", unit = "B", type = DeviceType.SENSOR, icon = "network" ),
                "cpu_temp": DeviceData("CPU Temperature", unit = "°C", type = DeviceType.SENSOR, icon = "thermometer" )
            })
        if self.settings.enableShutdown:
            self.data["shutdown"] = DeviceData("Shutdown PC", action=partial(self._device_command, "shutdown"), type = DeviceType.BUTTON, icon="power")
        if self.settings.enableReboot:
            self.data["reboot"] = DeviceData("Reboot PC", action=partial(self._device_command, "reboot"), type = DeviceType.BUTTON, icon="restart")


    def update_data(self, _mqtt_online: bool = False):
        if self.settings.enabled and self.settings.enableInfos:
            self.data["cpu_freq"].data = self._get_cpu_freq()
            self.data["memory_usage"].data = self._get_memory_usage_percent()
            self.data["cpu_load"].data = self._get_memory_usage_percent()
            self.data["disk_usage_root"].data = self._get_disk_usage_root_percent()
            self.data["disk_free_root"].data = self._get_disk_free_root_gb()
            self.data["net_bytes_sent"].data = self._get_net_bytes_sent()
            self.data["net_bytes_recv"].data = self._get_net_bytes_recv()
            self.data["cpu_temp"].data = self._get_cpu_temp_psutil()



    def _device_command(self, function, payload):
        logger.info("✏️  Device command: %s - %s", function, payload)
        if function == "shutdown": 
            Tools.shutdown()
        elif function == "reboot": 
            Tools.reboot()
        elif ( function == "test"): logger.info("🧪 Test command")
        else: logger.warning("⚠️  Unknown Device command: %s - %s", function, payload)


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
