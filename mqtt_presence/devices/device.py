
from abc import ABC, abstractmethod
from typing import Optional

from mqtt_presence.config.configuration import Configuration
from mqtt_presence.devices.device_data import DeviceData, DeviceKey


class Device(ABC):
    def __init__(self, devcie_key: DeviceKey):
        self._enabled: bool = True
        self._status: bool = False
        self._error_msg: str = ""
        self._device_key: DeviceKey = devcie_key
        self._data: dict[str, DeviceData] = {}


    @abstractmethod
    def init(self, config: Configuration, device_callback):
        self._reset_status()

    @abstractmethod
    def exit(self):
        self._reset_status()


    @abstractmethod
    def update_data(self, mqtt_online: Optional[bool] = None):
        pass

    @abstractmethod
    def handle_command(self, data_key: str, function: str):
        pass

    def _reset_status(self):
        self.data.clear()
        self._status = False
        self._error_msg = ""

    @property
    def device_key(self) -> DeviceKey:
        return self._device_key

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):  # Setter
        self._name = value    

    @property
    def data(self) -> dict[str, DeviceData]:
        return self._data

    @property
    def status(self) -> bool:
        return self._status

    @property
    def error_msg(self) -> str:
        return self._error_msg
