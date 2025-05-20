import logging


from mqtt_presence.app_data import RaspberryPiSettings, Gpio, GpioMode
from mqtt_presence.mqtt_presence_app import MQTTPresenceApp

logger = logging.getLogger(__name__)


class GpioHandler:
    def __init__(self, gpio):
        self.gpio = None
        self.gpio_zero = None
    
        from gpiozero import Button, LED, DigitalOutput, DigitalInput

        if self.gpio.mode == GpioMode.INPUT:
            gpio_zero = DigitalInput(gpio.number)
        if gpio.mode == GpioMode.OUTPUT:
            gpio_zero = DigitalOutput(gpio.number)
        if gpio.mode == GpioMode.LED:
            gpio_zero = LED(gpio.number)
        if gpio.mode == GpioMode.BUTTON:
            gpio_zero = Button(gpio.number)
            gpio_zero.when_pressed  = self.on_press

    def close(self):
        self.gpio_zero.close()

