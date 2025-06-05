import logging
from typing import List, Optional, Dict

from mqtt_presence.devices.raspberrypi.raspberrypi_data import RaspberryPiSettings
from mqtt_presence.devices.raspberrypi.raspberrypi_gpio_handler import GpioHandler
from mqtt_presence.devices.device_data import DeviceKey
from mqtt_presence.devices.device import Device
from mqtt_presence.config.configuration import Configuration


logger = logging.getLogger(__name__)



class RaspberryPiDevice(Device):
    def __init__(self, devcie_key: DeviceKey):
        super().__init__(devcie_key)
        self._gpio_handlers: Dict[str, GpioHandler] = {}


    def exit(self):
        super().exit()
        if self.status or len(self._gpio_handlers) > 0:
            logger.info("🔴 Stopping raspberrypi device")
            for gpio in self._gpio_handlers.values():
                gpio.close()
            self._gpio_handlers.clear()


    def init(self, config: Configuration, device_callback):
        self._error_msg = ""
        settings: RaspberryPiSettings = config.devices.raspberryPi
        if (not settings or settings.enabled is False):
            return
        
        try:
            logger.info("🟢 Initializing raspberrypi device")

            self._gpio_handlers.clear()
            for gpio in settings.gpios:
                gpio_handler = GpioHandler(gpio, self.device_key, device_callback)
                if gpio is not None:
                    self._gpio_handlers[gpio_handler.data_key] = gpio_handler
            logger.info("🍓 Created %s gpios", len(self._gpio_handlers))

            for gpio_handler in self._gpio_handlers.values():
                gpio_handler.create_data(self.data)
            
            self._status = True          
        except Exception as e:
            self._error_msg = str(e)
            logger.info("🔴 Raspberrypi failed: %s", e)
            self._gpio_handlers.clear()
            self._status = False


    def update_data(self, mqtt_online: Optional[bool] = None):
        for gpio_handler in self._gpio_handlers.values():
            gpio_handler.update_data(self.data, mqtt_online)


    def handle_command(self, data_key: str, function: str):
        self._gpio_handlers[data_key].command(self.device_key, data_key, function=function)
