import logging
from typing import List


from mqtt_presence.devices.raspberrypi.raspberrypi_data import RaspberryPiSettings,  Gpio, GpioMode
from mqtt_presence.devices.raspberrypi.raspberrypi_gpio_handler import GpioHandler
from mqtt_presence.mqtt.mqtt_data import MqttTopics

logger = logging.getLogger(__name__)



class RaspberryPiDevice:
    def __init__(self):
        self.gpio_handlers: List[GpioHandler] = []


    def exit(self):
        if self.gpio_handlers is not None:
            logger.info("🔴 Stopping raspberrypi device")
            ##call(['espeak "System shutdown" 2>/dev/null'], shell=True)
            for gpio in self.gpio_handlers:
                gpio.close()
            self.gpio_handlers = []


    def init(self, topic_callback): #, settings: RaspberryPiSettings, topic_callback):
        settings = self.get_test_config()
        if (not settings.enable_raspberrypi):
            return
        
        try:
            logger.info("🟢 Initializing raspberrypi device")

            self.gpio_handlers = []
            for gpio in settings.gpios:
                gpio_handler = GpioHandler(gpio, topic_callback, simulated=settings.simulated)
                if gpio is not None:
                    self.gpio_handlers.append(gpio_handler)
            logger.info("Created %s gpios", len(self.gpio_handlers))
          
        except Exception as e:
            logger.info("🔴 Raspberrypi failed: %s", e)
            self.gpio_handlers = []


            
    def create_topics(self, mqtt_topics: MqttTopics, prefix):
        for gpio_handler in self.gpio_handlers:
            gpio_handler.create_topic(mqtt_topics, prefix)


    def update_data(self, mqtt_topics: MqttTopics):
        for gpio_handler in self.gpio_handlers:
            gpio_handler.update_data(mqtt_topics)

 

    def get_gpio_handler(self, gpio_setting):
        return next((gpio for gpio in self.gpio_handlers if gpio.gpio == gpio_setting), None)



    def get_test_config(self):                
        settings:RaspberryPiSettings = RaspberryPiSettings()
        settings.enable_raspberrypi = True
        settings.simulated = False
        settings.gpios.append(Gpio(GpioMode.LED, 19, friendly_name = "Red"))
        settings.gpios.append(Gpio(GpioMode.LED, 21, friendly_name = "Blue"))
        settings.gpios.append(Gpio(GpioMode.BUTTON, 16, friendly_name = "Powerdown"))
        return settings