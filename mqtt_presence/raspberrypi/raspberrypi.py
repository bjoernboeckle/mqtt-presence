import logging

from mqtt_presence.app_data import RaspberryPiSettings, Gpio, GpioMode
from mqtt_presence.mqtt_presence_app import MQTTPresenceApp
from mqtt_presence.raspberrypi.raspberrypi_gpio_handler import GpioHandler

logger = logging.getLogger(__name__)



class RaspberryPiExtension:
    def __init__(self, mqtt_app: MQTTPresenceApp):
        self.mqtt_app = mqtt_app
        self.gpio_handlers = []

    def on_press():
        logger.info("pressed")


    def exit_raspberrypi(self):
        if self.current_settings is not None:
            logger.info("🔴 Stopping raspberrypi extension")
            ##call(['espeak "System shutdown" 2>/dev/null'], shell=True)
            for gpio in self.gpio_handlers:
                gpio.close()


    def init_raspberrypi(self):
        if (not self.mqtt_app.config.raspberry_pi.gpios.enable_raspberrypi):
            return
        
        try:
            logger.info("🟢 Initializing raspberrypi extension")
            #call(['espeak "Welcome to autodarts" 2>/dev/null'], shell=True)

            self.gpio_handlers = []
            for gpio in self.mqtt_app.config.raspberry_pi.gpios:
                gpio_handler = GpioHandler(gpio)
                if gpio is not None:
                    self.gpio_handlers.append(gpio_handler)
          
        except Exception as e:
            logger.info("🔴 Raspberrypi failed:", e)
            self.gpio_handlers = []


    def shutdown(self):
        print("Button shutdown!")
        self.mqtt_handler.disconnect()        
        self.helpers.shutdown()


