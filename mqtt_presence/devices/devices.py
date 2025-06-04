from collections import defaultdict
from typing import List, Optional, Dict

import logging

from mqtt_presence.devices.raspberrypi.raspberrypi_device import RaspberryPiDevice
from mqtt_presence.devices.pc_utils.pc_utils import PcUtils
from mqtt_presence.devices.device_data import DeviceData
from mqtt_presence.devices.device import Device
from mqtt_presence.config.configuration import Configuration

logger = logging.getLogger(__name__)


class Devices:
    def __init__(self):
            self.raspberrypi = RaspberryPiDevice("raspberrypi")
            self.pc_utils = PcUtils("pc_utils")
            self._devices: Dict[str, Device] = {
                self.raspberrypi.device_key: self.raspberrypi,
                self.pc_utils.device_key: self.pc_utils
            }
            self.devices_data = {
                self.raspberrypi.device_key: self.raspberrypi.data,
                self.pc_utils.device_key: self.pc_utils.data
            }            


    @property
    def devices(self) -> Dict[str, Device]:
        return self._devices            



    def init(self, config: Configuration, topic_callback):
        for device in self._devices.values():
            device.init(config, topic_callback)


    def exit(self):
        for device in self._devices.values():
            device.exit()


    def update_data(self,  mqtt_online: Optional[bool] = None):
        for device in self._devices.values():
            device.update_data(mqtt_online)


    def handle_command(self, device_key: str, data_key: str, function: str):
        device: Device = self.devices[device_key]
        device.handle_command(data_key, function)
