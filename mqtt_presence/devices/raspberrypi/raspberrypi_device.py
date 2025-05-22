import logging
from typing import List

from mqtt_presence.devices.raspberrypi.raspberrypi_data import RaspberryPiSettings, Gpio, GpioButton, GpioMode, GpioButton_Function
from mqtt_presence.devices.raspberrypi.raspberrypi_gpio_handler import GpioHandler
from mqtt_presence.mqtt.mqtt_data import MqttTopics
from mqtt_presence.devices.raspberrypi.raspberrypi_settings_yaml import RaspberryPiSettingsYaml

logger = logging.getLogger(__name__)



class RaspberryPiDevice:
    def __init__(self, config_path: str):
        self.gpio_handlers: List[GpioHandler] = []
        self.config_path = config_path


    def exit(self):
        if self.gpio_handlers is not None:
            logger.info("🔴 Stopping raspberrypi device")
            for gpio in self.gpio_handlers:
                gpio.close()
            self.gpio_handlers = []


    def init(self, topic_callback):
        settings = self.read_config()    
        if (not settings.enable_raspberrypi):
            return
        
        try:
            logger.info("🟢 Initializing raspberrypi device")

            self.gpio_handlers = []
            for gpio in settings.gpios:
                gpio_handler = GpioHandler(gpio, topic_callback, simulated=settings.simulated)
                if gpio is not None:
                    self.gpio_handlers.append(gpio_handler)
            logger.info("🍓 Created %s gpios", len(self.gpio_handlers))
          
        except Exception as e:
            logger.info("🔴 Raspberrypi failed: %s", e)
            self.gpio_handlers = []


    def create_topics(self, mqtt_topics: MqttTopics):
        for gpio_handler in self.gpio_handlers:
            gpio_handler.create_topic(mqtt_topics)


    def update_data(self, mqtt_topics: MqttTopics):
        for gpio_handler in self.gpio_handlers:
            gpio_handler.update_data(mqtt_topics)


    def get_gpio_handler(self, gpio_setting):
        return next((gpio for gpio in self.gpio_handlers if gpio.gpio == gpio_setting), None)


    def read_config(self):
        setting_file = f"{self.config_path}/raspberrypi.yaml"
        try:
            return RaspberryPiSettingsYaml.load_raspberry_settings(setting_file)
        except Exception as e:    
            logger.exception("🔴 read_config failed, create default")
            settings:RaspberryPiSettings = RaspberryPiSettings()
            settings.enable_raspberrypi = True
            settings.simulated = False
            settings.gpios.append(Gpio(GpioMode.LED, 19, friendly_name = "Red"))
            settings.gpios.append(Gpio(GpioMode.LED, 21, friendly_name = "Blue"))
            # Button
            button = Gpio(GpioMode.BUTTON, 16, friendly_name = "Powerdown")
            button.button = GpioButton()
            button.button.bounce_s = 0.1
            button.button.function_held = GpioButton_Function.SHUTDOWN
            settings.gpios.append(button)
            RaspberryPiSettingsYaml.save_raspberry_settings(settings, setting_file)
            return settings
