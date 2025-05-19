import platform
import sys
import logging


from mqtt_presence.mqtt_client import MQTTClient
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



    def update_new_config(self, config : Configuration):
        self.config_handler.save_config(config)
        self.restart()


    def start(self):
        #show platform
        self.log_platform()
        self.mqtt_client.start_mqtt()


    def restart(self):
        self.config = self.config_handler.load_config()
        self.mqtt_client.disconnect()

    def exit_app(self):
        self.should_run = False
        self.mqtt_client.disconnect()


    def shutdown(self):
        logger.info("🛑 Shutdown initiated...")
        if not self.app_config.app.disableShutdown:
            Tools.shutdown()
        else:
            logger.info("Shutdown disabled!")

    def reboot(self):
        logger.info("🔄 Reboot initiated...")
        if not self.app_config.app.disableShutdown:
            Tools.reboot()
        else:
            logger.info("Shutdown disabled!")

    @staticmethod
    def log_platform():
        system = platform.system()
        machine = platform.machine()

        if system == "Windows":
            logger.info("🪟 Running on Windows")
        elif system == "Linux":
            if "arm" in machine or "aarch64" in machine:
                logger.info("🍓 Running on Raspberry Pi (likely)")
            else:
                logger.info("🐧 Running on generic Linux")
        elif system == "Darwin":
            logger.info("🍏 Running on macOS")
        else:
            logger.warning("Unknown system: %s", system)
            sys.exit(1)
