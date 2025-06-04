
from abc import ABC, abstractmethod
from typing import Optional

from mqtt_presence.config.configuration import Configuration
from mqtt_presence.devices.device_data import DeviceData


class Device(ABC):
    def __init__(self, device_key):
        self._enabled = True
        self._device_key = device_key
        self._data: dict[str, DeviceData] = {}

    @abstractmethod
    def init(self, config: Configuration, topic_callback):
        pass

    @abstractmethod
    def exit(self):
        pass


    @abstractmethod
    def update_data(self, mqtt_online: Optional[bool] = None):
        pass

    @abstractmethod
    def handle_command(self, data_key: str, function: str):
        pass

    @property
    def device_key(self) -> str:
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
