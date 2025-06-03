
from abc import ABC, abstractmethod

from mqtt_presence.config.configuration import Configuration
from mqtt_presence.devices.device_data import DeviceData


class Device(ABC):
    def __init__(self, device_key):
        self._enabled = True
        self._device_key = device_key
        self._data: dict[str, DeviceData] = {}
        self._filtered_data: dict[str, DeviceData] = {}

    @abstractmethod
    def init(self, config: Configuration, topic_callback):
        pass

    @abstractmethod
    def exit(self):
        pass


    @abstractmethod
    def update_data(self, mqtt_online: bool = None):
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
    
    @property
    def filtered_data(self) -> dict[str, DeviceData]:
        return self._filtered_data
    

    def update_filterd_data(self):
        self._filtered_data = {
            key: { "data": value.data, "friendly_name": value.friendly_name, "unit": value.unit }
            for key, value in self._data.items()
            if value.data is not None
        }