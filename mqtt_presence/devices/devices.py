from collections import defaultdict
from typing import List, Optional, Dict

import logging

from mqtt_presence.devices.raspberrypi.raspberrypi_device import RaspberryPiDevice
from mqtt_presence.devices.pc_utils.pc_utils import PcUtils
from mqtt_presence.devices.device_data import DeviceKey, DeviceData
from mqtt_presence.devices.device import Device
from mqtt_presence.config.configuration import Configuration

logger = logging.getLogger(__name__)


class Devices:
    def __init__(self):
            devices = [
                RaspberryPiDevice(DeviceKey.RASPBERRY_PI),
                PcUtils(DeviceKey.PC_UTILS)
            ]
            self._devices: Dict[DeviceKey, Device] = {device.device_key: device for device in devices}

    @property
    def devices(self) -> Dict[DeviceKey, Device]:
        return self._devices


    def init(self, config: Configuration, device_callback):
        for device in self._devices.values():
            device.init(config, device_callback)


    def exit(self):
        for device in self._devices.values():
            device.exit()


    def update_data(self,  mqtt_online: Optional[bool] = None):
        for device in self._devices.values():
            device.update_data(mqtt_online)


    def handle_command(self, device_key: DeviceKey, data_key: str, function: str):
        device: Device = self.devices[device_key]
        device.handle_command(data_key, function)


    def get_device_status(self) -> Dict[DeviceKey, Dict[str, DeviceData]]:
        return {
                device_key.value: {
                    "status": device.status,
                    "error_msg": device.error_msg,
                    "data": device.data #if device.data is not None else {}
                }
                for device_key, device in self.devices.items()
            }
