
class MqttTopicsRaspberryPi:
    def __init__(self, helpers, config_handler, mqtt_handler, ):
        self.helpers = helpers
        self.config_handler = config_handler
        self.mqtt_handler = mqtt_handler        
        self.blueLED = None
        self.shutdown_btn = None
        self.status = "Not initialised"


    def exit_raspberrypi(self):
        self.status = "Exit raspberry pi extension."
        print(self.status)

        ##call(['espeak "System shutdown" 2>/dev/null'], shell=True)
        if ( self.blueLED is not None ): self.blueLED.off()
        self.blueLED = None
        self.shutdown_btn = None
        self.status = "Stopped"



    def init_raspberrypi(self):
        self.exit_raspberrypi()
        try:            
            if (self.config_handler.config["enable_raspberrypi"] ):
                self.status = "Initialising raspberry pi extension..."
                print(self.status)

                from gpiozero import Button
                from gpiozero import LED
                
                #call(['espeak "Welcome to autodarts" 2>/dev/null'], shell=True)
                #LED
                ledGpio =  int(self.config_handler.config.get("gpio_led", -1))
                self.status = f"Setup LED...{ledGpio}"
                print(self.status)        
                if (ledGpio >= 0):
                    self.blueLED = LED(ledGpio)
                    self.blueLED.on()
                else:
                    self.blueLED = None

                #Button
                buttonGpio =  int(self.config_handler.config.get("gpio_button", -1))
                self.status = f"Setup Button...{buttonGpio}"
                print(self.status)        

                if (buttonGpio >= 0 ):
                    self.shutdown_btn = Button(buttonGpio, hold_time=2)
                    self.shutdown_btn.when_held = self.shutdown
                else:
                    self.shutdown_btn = None

        except Exception as e:
            self.status = f"Raspberrypi failed: {e}"
            print(self.status)


    def shutdown(self):
        print("Button shutdown!")
        self.mqtt_handler.disconnect()        
        self.helpers.shutdown()


