import logging
from functools import partial

from mqtt_presence.app_data import Gpio, GpioMode


logger = logging.getLogger(__name__)


class GPioZeroSimulated():
    def __init__(self):
        self.when_pressed = None


class GpioHandler:
    def __init__(self, gpio : Gpio, button_callback, simulated=False):
        self.gpio = gpio
        self.gpio_zero = None
        if simulated :
            if self.gpio.mode == GpioMode.INPUT:
                pass
            elif gpio.mode == GpioMode.OUTPUT:
                pass
            elif gpio.mode == GpioMode.LED:
                pass
            elif gpio.mode == GpioMode.BUTTON:
                self.gpio_zero = GPioZeroSimulated()
                self.gpio_zero.when_pressed  = button_callback
        else:
            from gpiozero import Button, LED

            if self.gpio.mode == GpioMode.INPUT:
                pass    #self.gpio_zero = DigitalInput(gpio.number)
            elif gpio.mode == GpioMode.OUTPUT:
                pass    #self.gpio_zero = DigitalOutput(gpio.number)
            elif gpio.mode == GpioMode.LED:
                self.gpio_zero = LED(gpio.number)
            elif gpio.mode == GpioMode.BUTTON:
                self.gpio_zero = Button(gpio.number)
                self.gpio_zero.when_pressed  = partial(button_callback, gpio.number)


    def simulate_button(self):
        self.gpio_zero.when_pressed(self.gpio)


    def get_led(self):
        if self.gpio_zero is not None:
            return self.gpio_zero.value
        return -1
          


    def set_led(self, state: bool):
        if (self.gpio_zero is not None):
            if state:
                self.gpio_zero.on()
            else:
                self.gpio_zero.off()
        else:
            logger.info("GPIO %s not available, simualted %s", self.gpio.friendly_name, state)


    def close(self):
        if (self.gpio_zero is not None):
            self.gpio_zero.close()

