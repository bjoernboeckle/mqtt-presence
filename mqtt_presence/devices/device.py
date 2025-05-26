
from abc import ABC, abstractmethod

from mqtt_presence.config.configuration import Configuration
from mqtt_presence.devices.device_data import DeviceData


class Device(ABC):
    def __init__(self):
        self._enabled = True
        self._data: dict[str, DeviceData] = {}
        self._filtered_data: dict[str, DeviceData] = {}

    @abstractmethod
    def init(self, config: Configuration, topic_callback):
        pass

    @abstractmethod
    def exit(self):
        pass


    @abstractmethod
    def update_data(self):
        pass


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
    def filtered_data(self) -> dict[str, DeviceData]:
        return self._filtered_data
    

    def update_filterd_data(self):
        self._filtered_data = {
            key: value
            for key, value in self._data.items()
            if value.data is not None
        }