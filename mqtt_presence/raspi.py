import time

from mqtt_presence.raspberrypi.raspberrypi import RaspberryPiExtension
from mqtt_presence.raspberrypi.raspberrypi_gpio_handler import GpioHandler
from mqtt_presence.app_data import RaspberryPiSettings, Gpio, GpioMode
from mqtt_presence.app_data import Gpio



settings:RaspberryPiSettings = RaspberryPiSettings()
settings.enable_raspberrypi = True
settings.simulated = False
settings.gpios.append(Gpio(GpioMode.LED, 19, friendly_name = "Red"))
settings.gpios.append(Gpio(GpioMode.LED, 21, friendly_name = "Blue"))
settings.gpios.append(Gpio(GpioMode.BUTTON, 27, friendly_name = "Powerdown"))



def callback(gpio: Gpio):
    print("Callback")

extension = RaspberryPiExtension()
extension.init_raspberrypi(settings, callback)

print("Wait-----")
time.sleep(1)
print("Simulate button")


handler = extension.get_gpio_handler(settings.gpios[2])
handler.simulate_button()

print("Wait key")

while True:
    time.sleep(1)