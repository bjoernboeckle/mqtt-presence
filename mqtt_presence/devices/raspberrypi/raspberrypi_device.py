import logging
from typing import List

from mqtt_presence.devices.raspberrypi.raspberrypi_data import RaspberryPiSettings
from mqtt_presence.devices.raspberrypi.raspberrypi_gpio_handler import GpioHandler
from mqtt_presence.mqtt.mqtt_data import MqttTopic
from mqtt_presence.config.configuration import Configuration

logger = logging.getLogger(__name__)



class RaspberryPiDevice:
    def __init__(self):
        self.gpio_handlers: List[GpioHandler] = []


    def exit(self):
        if self.gpio_handlers is not None:
            logger.info("🔴 Stopping raspberrypi device")
            for gpio in self.gpio_handlers:
                gpio.close()
            self.gpio_handlers = []


    def init(self, config: Configuration, topic_callback):
        settings: RaspberryPiSettings = config.devices.raspberryPi
        if (not settings or settings.enabled is False):
            return
        
        try:
            logger.info("🟢 Initializing raspberrypi device")

            self.gpio_handlers = []
            for gpio in settings.gpios:
                gpio_handler = GpioHandler(gpio, topic_callback)
                if gpio is not None:
                    self.gpio_handlers.append(gpio_handler)
            logger.info("🍓 Created %s gpios", len(self.gpio_handlers))
          
        except Exception as e:
            logger.info("🔴 Raspberrypi failed: %s", e)
            self.gpio_handlers = []


    def create_topics(self) -> dict[str, MqttTopic]:
        result: dict[str, MqttTopic] = {}
        for gpio_handler in self.gpio_handlers:
            gpio_handler.create_topic(result)
        return result


    def update_data(self, device_data: dict[str, str]):
        for gpio_handler in self.gpio_handlers:
            gpio_handler.update_data(device_data)


    def get_gpio_handler(self, gpio_setting):
        return next((gpio for gpio in self.gpio_handlers if gpio.gpio == gpio_setting), None)


  