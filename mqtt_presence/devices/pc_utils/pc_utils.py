import logging
from typing import Optional
import psutil
import socket


from mqtt_presence.devices.device_data import DeviceData, DeviceType
from mqtt_presence.config.configuration import Configuration
from mqtt_presence.utils import Tools
from mqtt_presence.devices.pc_utils.pc_utils_data import PcUtilsSettings
from mqtt_presence.devices.device import Device
from mqtt_presence.devices.device_data import DeviceKey

logger = logging.getLogger(__name__)


class PcUtils(Device):
    def __init__(self, devcie_key: DeviceKey):
        super().__init__(devcie_key)


    def exit(self):
        super().exit()



    def init(self, config: Configuration, device_callback):
        super().init(config, device_callback)
        self.settings: PcUtilsSettings = config.devices.pc_utils
        if not self.settings.enabled:
            self._error_msg = "PC Utils device is disabled in the configuration. Apply to enable it."
            return

        self._status = True
        if self.settings.enableInfos:
            self.data.update( {
                # MQTT buttons
                #"test": DeviceData(friendly_name="Test button", type = DeviceType.BUTTON, icon="test-tube"),
                # MQTT sensors
                "ip_address": DeviceData(friendly_name="IP Addresses", type = DeviceType.SENSOR, icon = "ip"),
                "cpu_freq": DeviceData(friendly_name="CPU Frequency", unit = "MHz", type = DeviceType.SENSOR, icon = "sine-wave"),
                "memory_usage": DeviceData(friendly_name="RAM Usage", unit = "%", type = DeviceType.SENSOR, icon = "memory" ),
                "cpu_load": DeviceData(friendly_name="CPU Load (1 min avg)", unit = "%", type = DeviceType.SENSOR, icon = "gauge" ),
                "disk_usage_root": DeviceData(friendly_name="Disk Usage", unit = "%", type = DeviceType.SENSOR, icon = "harddisk"),
                "disk_free_root": DeviceData(friendly_name="Disk Free Space", unit = "GB", type = DeviceType.SENSOR, icon = "harddisk" ),
                "net_bytes_sent": DeviceData(friendly_name="Network Bytes Sent", unit = "B", type = DeviceType.SENSOR, icon = "network" ),
                "net_bytes_recv": DeviceData(friendly_name="Network Bytes Received", unit = "B", type = DeviceType.SENSOR, icon = "network" ),
                "cpu_temp": DeviceData(friendly_name="CPU Temperature", unit = "°C", type = DeviceType.SENSOR, icon = "thermometer" )
            })
        if self.settings.enableShutdown:
            self.data["shutdown"] = DeviceData(friendly_name="Shutdown PC", type = DeviceType.BUTTON, icon="power")
        if self.settings.enableReboot:
            self.data["reboot"] = DeviceData(friendly_name="Reboot PC", type = DeviceType.BUTTON, icon="restart")


    def update_data(self, mqtt_online: Optional[bool] = False):
        if self.settings.enabled and self.settings.enableInfos:
            self.data["ip_address"].data = ", ".join(self._get_all_ips())
            self.data["cpu_freq"].data = str(self._get_cpu_freq())
            self.data["memory_usage"].data = str(self._get_memory_usage_percent())
            self.data["cpu_load"].data = str(self._get_memory_usage_percent())
            self.data["disk_usage_root"].data = str(self._get_disk_usage_root_percent())
            self.data["disk_free_root"].data = str(self._get_disk_free_root_gb())
            self.data["net_bytes_sent"].data = str(self._get_net_bytes_sent())
            self.data["net_bytes_recv"].data = str(self._get_net_bytes_recv())
            self.data["cpu_temp"].data = str(self._get_cpu_temp_psutil())


    def handle_command(self, data_key: str, function: str):
        logger.info("✏️  Device command: %s - %s", data_key, function)
        if data_key == "shutdown":
            Tools.shutdown()
        elif data_key == "reboot":
            Tools.reboot()
        elif ( data_key == "test"):
            logger.info("🧪 Test command")
        else:
            logger.warning("⚠️  Unknown Device command: %s - %s", data_key, function)



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
        if not hasattr(psutil, "sensors_temperatures"):
            return None
        try:
            for _, entries in psutil.sensors_temperatures().items(): # type: ignore
                for entry in entries:
                    if entry.label in ("Package id 0", "", None):
                        return entry.current
        except Exception:
            return None
        return None

    def _get_ip_address(self):
        return socket.gethostbyname(socket.gethostname())
    

    def _get_all_ips(self):
        ip_list = []
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:  # Nur IPv4-Adressen
                    ip_list.append(addr.address)
        return ip_list