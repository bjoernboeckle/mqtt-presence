from dataclasses import dataclass

from mqtt_presence.devices.device_data import DeviceSettings

@dataclass
class PcUtilsSettings(DeviceSettings):
    enableShutdown: bool = True
    enableReboot: bool = True
    enableInfos: bool = True
