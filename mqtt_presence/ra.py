# pylint: skip-file

from gpiozero import Button
#from gpiozero.pins.rpigpio import RPiGPIOFactory
from signal import pause

# Nutzt explizit RPi.GPIO statt automatisch
#factory = RPiGPIOFactory()
button = Button(16) #, pin_factory=factory)

def on_press():
    print("Button gedrückt")

button.when_pressed = on_press

pause()
