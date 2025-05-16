import platform
import sys
import logging


from mqtt_presence.mqtt_client import MQTTClient
from mqtt_presence.config_handler import ConfigHandler
from mqtt_presence.app_data import Configuration, ConfigFiles
from mqtt_presence.utils import Tools
from mqtt_presence.version import __version__

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
    def __init__(self, config_file = ConfigFiles()):
        # set singleton!
        #AppStateSingleton.init(self)
        self.version = __version__

        self.config_handler = ConfigHandler(config_file)
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
        self.mqtt_client.start()


    def restart(self):
        self.config = self.config_handler.load_config()
        self.mqtt_client.stop()

    def exit_app(self):
        self.should_run = False
        self.mqtt_client.stop()


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
