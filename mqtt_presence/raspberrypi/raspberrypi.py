import logging

from mqtt_presence.app_data import RaspberryPiSettings, Gpio, GpioMode
from mqtt_presence.raspberrypi.raspberrypi_gpio_handler import GpioHandler

logger = logging.getLogger(__name__)



class RaspberryPiExtension:
    def __init__(self):
        self.gpio_handlers = []


    def exit_raspberrypi(self):
        if self.gpio_handlers is not None:
            logger.info("🔴 Stopping raspberrypi extension")
            ##call(['espeak "System shutdown" 2>/dev/null'], shell=True)
            for gpio in self.gpio_handlers:
                gpio.close()
            self.gpio_handlers = []


    def init_raspberrypi(self, settings: RaspberryPiSettings, button_callback):
        if (not settings.enable_raspberrypi):
            return
        
        try:
            logger.info("🟢 Initializing raspberrypi extension")
            #call(['espeak "Welcome to autodarts" 2>/dev/null'], shell=True)

            self.gpio_handlers = []
            for gpio in settings.gpios:
                gpio_handler = GpioHandler(gpio, button_callback, simulated=settings.simulated)
                if gpio is not None:
                    self.gpio_handlers.append(gpio_handler)
          
        except Exception as e:
            logger.info("🔴 Raspberrypi failed: %s", e)
            self.gpio_handlers = []



    def get_gpio_handler(self, gpio_setting):
        return next((gpio for gpio in self.gpio_handlers if gpio.gpio == gpio_setting), None)


