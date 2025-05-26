import logging
from functools import partial

from mqtt_presence.devices.raspberrypi.raspberrypi_data import Gpio, GpioMode, GpioButton, GpioButton_Function
from mqtt_presence.devices.device_data import DeviceData, Homeassistant, HomeassistantType
from mqtt_presence.utils import Tools

logger = logging.getLogger(__name__)


PRESSED = "button_short_press"
RELEASED = "button_short_release"
HELD = "button_long_press"

class GpioHandler:
    def __init__(self, gpio : Gpio, action_callback):
        self.gpio = gpio
        self.gpio_zero = None
        self.gpio_key = f"gpio_{self.gpio.number}"
        self._action_callback = action_callback


        from gpiozero import Button, LED
        if gpio.mode == GpioMode.LED:
            self.gpio_zero = LED(gpio.number)
        elif gpio.mode == GpioMode.BUTTON:
            button: GpioButton = gpio.button if gpio.button is not None else GpioButton()
            self.gpio_zero = Button(gpio.number, bounce_time=button.bounce_s, pull_up=button.pull_up)
            self.gpio_zero.when_pressed  = partial(self._button_callback, self.gpio_key, PRESSED)
            self.gpio_zero.when_released  = partial(self._button_callback, self.gpio_key, RELEASED)
            self.gpio_zero.when_held  = partial(self._button_callback, self.gpio_key, HELD)
        else:
            logger.warning("⚠️ Not supported gpio mode %s", gpio.mode)
        #except Exception as e:
        #    logger.exception("🔴 Raspberry Pi failed")



    def get_button_function(self, func, button: GpioButton):
        if button is None:
            return None
        if button.function_held is not None and func == HELD:
            return button.function_held
        if button.function_released is not None and func == RELEASED:
            return button.function_released
        if button.function_pressed is not None and func == PRESSED:
            return button.function_pressed
        return None



    def _button_callback(self, gpio_key, function):
        self._action_callback(gpio_key, function)
        command = self.get_button_function(function, self.gpio.button)
        if (command is not None):
            if command ==  GpioButton_Function.REBOOT: Tools.reboot()
            elif command ==  GpioButton_Function.SHUTDOWN: Tools.shutdown()


    def get_led(self):
        if self.gpio_zero is not None:
            return self.gpio_zero.value
        return -1


    def set_led(self, state: int):
        if (self.gpio_zero is not None):
            if state != 0:
                self.gpio_zero.on()
            else:
                self.gpio_zero.off()


    def create_data(self, device_data: dict[str, DeviceData]):
        if self.gpio.mode == GpioMode.LED:
            device_data[self.gpio_key] = DeviceData(f"Led {self.gpio.number}", action=partial(self.command, "switch"), homeassistant=Homeassistant(type=HomeassistantType.SWITCH))
            #mqtt_topics.buttons[f"gpio_{self.gpio.number}_on"] = MqttTopic(f"{self.gpio.mode} {self.gpio.number} on", action=partial(self.command, "on"))
            #mqtt_topics.buttons[f"gpio_{self.gpio.number}_off"] = MqttTopic(f"{self.gpio.mode} {self.gpio.number} off", action=partial(self.command, "off"))
        elif self.gpio.mode == GpioMode.BUTTON:
            device_data[self.gpio_key] = DeviceData(f"GPIO {self.gpio.number} action", homeassistant=Homeassistant(type=HomeassistantType.DEVICE_AUTOMATION, actions = [PRESSED, RELEASED, HELD]))
        

    def update_data(self, device_data: dict[str, str]):
        if self.gpio.mode == GpioMode.LED:
            device_data[self.gpio_key].data = "OFF" if self.get_led() == 0 else "ON"



    def command(self, function, payload):
        if (self.gpio.mode == GpioMode.LED):
            if (function == "on"): self.set_led(1)
            elif (function == "off"): self.set_led(0)
            elif (function == "switch"):
                self.set_led(0 if payload == "off" else 1)
                self._action_callback(None, function)


    def close(self):
        if (self.gpio_zero is not None):
            self.gpio_zero.close()
