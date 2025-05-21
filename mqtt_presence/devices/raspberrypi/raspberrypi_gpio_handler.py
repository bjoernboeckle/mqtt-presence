import logging
from functools import partial

from mqtt_presence.devices.raspberrypi.raspberrypi_data import Gpio, GpioMode, GpioButton
from mqtt_presence.mqtt.mqtt_data import MqttTopics, MqttTopic

logger = logging.getLogger(__name__)


class GPioZeroSimulated():
    def __init__(self):
        self.when_pressed = None


class GpioHandler:
    def __init__(self, gpio : Gpio, topic_callback, simulated=False):
        self.gpio = gpio
        self.gpio_zero = None
        self.topic = f"gpio_{self.gpio.number}"
        if simulated :
            if self.gpio.mode == GpioMode.INPUT:
                pass
            elif gpio.mode == GpioMode.OUTPUT:
                pass
            elif gpio.mode == GpioMode.LED:
                pass
            elif gpio.mode == GpioMode.BUTTON:
                self.gpio_zero = GPioZeroSimulated()
                self.gpio_zero.when_pressed  = partial(topic_callback, self.topic)

        else:
            from gpiozero import Button, LED

            if self.gpio.mode == GpioMode.INPUT:
                pass    #self.gpio_zero = DigitalInput(gpio.number)
            elif gpio.mode == GpioMode.OUTPUT:
                pass    #self.gpio_zero = DigitalOutput(gpio.number)
            elif gpio.mode == GpioMode.LED:
                self.gpio_zero = LED(gpio.number)
            elif gpio.mode == GpioMode.BUTTON:
                button: GpioButton = gpio.button if gpio.button is not None else GpioButton()
                self.gpio_zero = Button(gpio.number, bounce_time=button.bounce_s, pull_up=button.pull_up)
                self.gpio_zero.when_pressed  = partial(topic_callback, self.topic, "pressed")
                self.gpio_zero.when_released  = partial(topic_callback, self.topic, "released")
                self.gpio_zero.when_held  = partial(topic_callback, self.topic, "held")


    def simulate_button(self):
        self.gpio_zero.when_pressed(self.gpio)


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
        else:
            logger.info("GPIO %s not available, simualted %s", self.gpio.friendly_name, state)



    def create_topic(self, mqtt_topics: MqttTopics, prefix):
        if self.gpio.mode == GpioMode.LED:
            mqtt_topics.switches[self.topic] = MqttTopic(f"Led {self.gpio.number}", action=partial(self.command, "switch"))
            #mqtt_topics.buttons[f"gpio_{self.gpio.number}_on"] = MqttTopic(f"{self.gpio.mode} {self.gpio.number} on", action=partial(self.command, "on"))
            #mqtt_topics.buttons[f"gpio_{self.gpio.number}_off"] = MqttTopic(f"{self.gpio.mode} {self.gpio.number} off", action=partial(self.command, "off"))
            #mqtt_topics.switches[f"gpio_{self.gpio.number}_switch"] = MqttTopic(f"Switch Led {self.gpio.number}", action=partial(self.command, "switch"))
        elif self.gpio.mode == GpioMode.BUTTON:
            print(f"Creating automation  -   gpio_{self.gpio.number}")
            mqtt_topics.device_automations[self.topic] = MqttTopic(f"Press", subtype = "pressed")
            mqtt_topics.device_automations[f"{self.topic}_released"] = MqttTopic(f"released", subtype = "released")
            mqtt_topics.device_automations[f"{self.topic}_held"] = MqttTopic(f"held", subtype = "held")


    def update_data(self, mqtt_topics: MqttTopics):
        if self.gpio.mode == GpioMode.LED:
            mqtt_topics.data[self.topic] = "OFF" if self.get_led() == 0 else "ON"



    def command(self, function, payload):
        print(f"payload: {payload}   function: {function} ")
        if (self.gpio.mode == GpioMode.LED):
            if (function == "on"): self.set_led(1)
            elif (function == "off"): self.set_led(0)
            elif (function == "switch"):
                self.set_led(0 if payload == "off" else 1)


    def close(self):
        if (self.gpio_zero is not None):
            self.gpio_zero.close()

