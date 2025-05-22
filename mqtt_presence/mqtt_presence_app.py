import logging

from mqtt_presence.mqtt.mqtt_client import MQTTClient
from mqtt_presence.devices.devices import Devices
from mqtt_presence.config_handler import ConfigHandler
from mqtt_presence.app_data import Configuration
from mqtt_presence.utils import Tools
from mqtt_presence.version import NAME, VERSION, AUTHORS, REPOSITORY, DESCRIPTION



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
        self.devices = Devices(self.config_handler.data_path)


    def update_new_config(self, config : Configuration):
        self.config_handler.save_config(config)
        self.config = config
        self.restart()


    def start(self):
        #show platform
        Tools.log_platform()
        self.devices.init(self._action_callback)
        self.mqtt_client.start_mqtt()




    def restart(self):
        print("ReStart!!!")
        self.config = self.config_handler.load_config()
        self.mqtt_client.disconnect()


    def exit_app(self):
        self.should_run = False
        self.mqtt_client.disconnect()
        self.devices.exit()



    def _action_callback(self, topic, function):
        logger.info("🚪 Callback: %s: %s", topic, function)
        self.mqtt_client.handle_action_callback(topic, function)
