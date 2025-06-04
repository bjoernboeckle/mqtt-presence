import logging
from functools import partial
from typing import Optional

from mqtt_presence.devices.raspberrypi.raspberrypi_data import Gpio, GpioMode, GpioButton, GpioLed, GpioButton_Function, GpioLed_Mode, GpioLed_Function
from mqtt_presence.devices.device_data import DeviceData, DeviceType
from mqtt_presence.utils import Tools

logger = logging.getLogger(__name__)


PRESSED = "button_short_press"
RELEASED = "button_short_release"
HELD = "button_long_press"

class GpioHandler:
    def __init__(self, gpio : Gpio, device_key, device_callback):
        self.gpio = gpio
        self._gpio_zero = None
        self._data_key = f"gpio_{self.gpio.number}"
        self._device_callback = device_callback
        self._device_key = device_key
        self.led_state = -1

        logger.info("✏️ Init Gpio %s - %s", gpio.number, gpio.mode)
        from gpiozero import Button, LED # type: ignore
        if gpio.mode == GpioMode.LED:
            self.led_state = -1
            led: GpioLed = gpio.led if gpio.led is not None else GpioLed()
            self._gpio_zero = LED(gpio.number)
            if led.led_function == GpioLed_Function.RUNNING:
                self.set_led(1)
        elif gpio.mode == GpioMode.BUTTON:
            button: GpioButton = gpio.button if gpio.button is not None else GpioButton()
            self._gpio_zero = Button(gpio.number, bounce_time=button.bounce_s, pull_up=button.pull_up)
            self._gpio_zero.when_pressed  = partial(self._button_callback, PRESSED)
            self._gpio_zero.when_released  = partial(self._button_callback, RELEASED)
            self._gpio_zero.when_held  = partial(self._button_callback, HELD)
        else:
            logger.warning("⚠️ Not supported gpio mode %s", gpio.mode)
        #except Exception as e:
        #    logger.exception("🔴 Raspberry Pi failed")



    def get_button_function(self, func, button: Optional[GpioButton]):
        if button is None:
            return None
        if button.function_held is not None and func == HELD:
            return button.function_held
        if button.function_released is not None and func == RELEASED:
            return button.function_released
        if button.function_pressed is not None and func == PRESSED:
            return button.function_pressed
        return None



    def _button_callback(self, function):
        self._device_callback(self._device_key, self._data_key, function)
        command = self.get_button_function(function, self.gpio.button)
        if (command is not None):
            if command ==  GpioButton_Function.REBOOT: 
                Tools.reboot()
            elif command ==  GpioButton_Function.SHUTDOWN: 
                Tools.shutdown()


    def get_led(self) -> int:
        if self._gpio_zero is not None and self.gpio.led is not None:
            if self.gpio.led.led_mode == GpioLed_Mode.BLINK:
                return self.led_state
            return self._gpio_zero.value
        return -1


    def set_led(self, state: int):
        if self.led_state == state:
            return
        if (self._gpio_zero is not None):           
            if state != 0:
                if self.gpio.led is not None and self.gpio.led.led_mode == GpioLed_Mode.BLINK:
                    self._gpio_zero.blink()
                else:
                    self._gpio_zero.on()
            else:
                self._gpio_zero.off()
        self.led_state = state


    def create_data(self, device_data: dict[str, DeviceData]):
        if self.gpio.mode == GpioMode.LED:
            device_data[self._data_key] = DeviceData(friendly_name=self.gpio.friendly_name, type = DeviceType.SWITCH, icon="led-variant-outline")       #f"Led {self.gpio.number}"
        elif self.gpio.mode == GpioMode.BUTTON:
            device_data[self._data_key] = DeviceData(friendly_name=self.gpio.friendly_name, type = DeviceType.DEVICE_AUTOMATION, icon="button-cursor", actions = [PRESSED, RELEASED, HELD])  #friendly_name=f"GPIO {self.gpio.number} action"
        

    def update_data(self, device_data: dict[str, DeviceData], mqtt_online: Optional[bool] = None):
        if self.gpio.mode == GpioMode.LED:
            if self.gpio.led is not None:
                if  mqtt_online is not None and self.gpio.led.led_function == GpioLed_Function.MQTT_ONLINE:                   
                    self.set_led(1 if mqtt_online else 0)
                if self.gpio.led.led_function == GpioLed_Function.RUNNING:
                    self.set_led(1)
            device_data[self._data_key].data = "off" if self.get_led() == 0 else "on"



 

    def command(self, function):
        logger.info("✏️ GPIO command %s function  %s", self.gpio.number,  function)
        if (self.gpio.mode == GpioMode.LED):
            self.set_led(0 if function == "off" else 1)
            self._device_callback()  # just trigger update
        elif (self.gpio.mode == GpioMode.BUTTON):        
            if function == PRESSED:
                self._button_callback(PRESSED)
            elif function == RELEASED:
                self._button_callback(RELEASED)
            elif function == HELD:
                self._button_callback(HELD)
            


    def close(self):
        logger.info("✏️ Close Gpio %s", self.gpio.number)
        if (self._gpio_zero is not None):
            self._gpio_zero.close()

    @property
    def data_key(self) -> str:
        return self._data_key
