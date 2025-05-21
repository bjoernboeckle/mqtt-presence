import logging

from mqtt_presence.mqtt_client import MQTTClient
from mqtt_presence.config_handler import ConfigHandler
from mqtt_presence.app_data import Configuration
from mqtt_presence.utils import Tools
from mqtt_presence.version import NAME, VERSION, AUTHORS, REPOSITORY, DESCRIPTION
from mqtt_presence.raspberrypi.raspberrypi import RaspberryPiExtension

logger = logging.getLogger(__name__)

# app_state_singleton.py
#class MQTTPresenceAppSingleton:
#    _instance = None
#
#    @classmethod
#    def init(cls, app_state):
#        cls._instance = app_state
#
#    @classmethod
#    def get(cls):
#        if cls._instance is None:
#            raise Exception("MQTTPresenceApp wurde noch nicht initialisiert!")
#        return cls._instance


class MQTTPresenceApp():
    NAME = NAME
    VERSION = VERSION
    AUTHORS = AUTHORS
    REPOSITORY = REPOSITORY
    DESCRIPTION = DESCRIPTION

    def __init__(self, data_path: str = None):
        # set singleton!
        #AppStateSingleton.init(self)

        self.config_handler = ConfigHandler(data_path)
        self.should_run = True

        # load config
        self.config = self.config_handler.load_config()
        self.app_config = self.config_handler.load_config_yaml()

        self.mqtt_client: MQTTClient = MQTTClient(self)
        self.raspberrypi = RaspberryPiExtension()


    def button_callback(self, gpio):
        logger.info("GPIO: %s pressed", gpio.number)


    def update_new_config(self, config : Configuration):
        self.config_handler.save_config(config)
        self.config = config
        self.restart()


    def start(self):
        #show platform
        Tools.log_platform()
        self.mqtt_client.start_mqtt()
        self.raspberrypi.init_raspberrypi(self.config.raspberry_pi, self.button_callback)



    def restart(self):
        self.raspberrypi.exit_raspberrypi()
        self.config = self.config_handler.load_config()
        self.mqtt_client.disconnect()
        self.raspberrypi.init_raspberrypi(self.config.raspberry_pi, self.button_callback)


    def exit_app(self):
        self.should_run = False
        self.mqtt_client.disconnect()
        self.raspberrypi.exit_raspberrypi()
