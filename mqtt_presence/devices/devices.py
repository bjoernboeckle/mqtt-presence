from collections import defaultdict
from typing import List

import logging

from mqtt_presence.devices.raspberrypi.raspberrypi_device import RaspberryPiDevice
from mqtt_presence.devices.pc_utils.pc_utils import PcUtils
from mqtt_presence.devices.device_data import DeviceData
from mqtt_presence.devices.device import Device
from mqtt_presence.config.configuration import Configuration

logger = logging.getLogger(__name__)


class Devices:
    def __init__(self):
            self.raspberrypi = RaspberryPiDevice()
            self.pc_utils = PcUtils()
            self._devices: dict[str, Device] = {
                "raspberrypi": self.raspberrypi,
                "pc_utils": self.pc_utils
            }
            #self._devices_data: dict[str, dict[str, DeviceData]] = []

    @property
    def devices(self) -> dict[str, Device]:
        return self._devices            



    def init(self, config: Configuration, topic_callback):
        for device in self._devices.values():
            device.init(config, topic_callback)
        
        #self._devices_data = {
        #    "RaspberryPiDevice": self.raspberrypi,
        #    "PcUtils": self.pc_utils
        #}
        #self._devices_data = {
        #    type(device).__name__: device.device_data
        #    for device in self._devices
        #}


    def exit(self):
        for device in self._devices.values():
            device.exit()


    def update_data(self, update_filered: bool = False):
        for device in self._devices.values():
            device.update_data()
            if update_filered:
                device.update_filterd_data()


    def get_devices_data(self) -> dict[str, dict[str, DeviceData]]:
        return {
            "raspberrypi": self.raspberrypi.filtered_data,
            "pc_utils": self.pc_utils.filtered_data
        }
        #return {
        #    type(device).__name__: device.device_data
        #    for device in self._devices
        #}