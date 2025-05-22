# pylint: skip-file

import time

from mqtt_presence.raspberrypi.raspberrypi import RaspberryPiDevice
from mqtt_presence.raspberrypi.raspberrypi_gpio_handler import GpioHandler
from mqtt_presence.app_data import RaspberryPiSettings, Gpio, GpioMode
from mqtt_presence.app_data import Gpio
from mqtt_presence.utils import Tools



settings:RaspberryPiSettings = RaspberryPiSettings()
settings.enable_raspberrypi = True
settings.simulated = False
settings.gpios.append(Gpio(GpioMode.LED, 19, friendly_name = "Red"))
settings.gpios.append(Gpio(GpioMode.LED, 21, friendly_name = "Blue"))
settings.gpios.append(Gpio(GpioMode.BUTTON, 16, friendly_name = "Powerdown"))

# set log directory
Tools.setup_logger(__name__, "./log")


def callback(gpio: Gpio):
    print("Callback")

extension = RaspberryPiDevice()
extension.init_raspberrypi(settings, callback)


print(f"{len(extension.gpio_handlers)}")

ledRed = extension.get_gpio_handler(settings.gpios[0])
ledBlue = extension.get_gpio_handler(settings.gpios[1])
btnPowerDown = extension.get_gpio_handler(settings.gpios[2])


print(ledRed)
print(btnPowerDown)

ledRed.set_led(1)# if ledRed.get_led() == 0 else 0)


print("Wait 3s")
time.sleep(3)

print("Updating LEDs")
ledRed.set_led(1 if ledRed.get_led() == 0 else 0)
ledBlue.set_led(1 if ledBlue.get_led() == 0 else 0)



print("Wait key")

while True:
    time.sleep(1)
    