from mqtt_presence.mqtt_client import MQTTClient
from mqtt_presence.config_handler import Config_Handler
from mqtt_presence.app_data import Configuration, ConfigFiles
from mqtt_presence.utils import Tools


import platform, sys
import logging
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
    def __init__(self, configFile = ConfigFiles()):
        # set singleton!
        #AppStateSingleton.init(self)
        self.version = Tools.get_version_from_pyproject("pyproject.toml")


        self.config_handler = Config_Handler(configFile)
        self.should_run = True
        
        # load config
        self.loadConfig()
        self.mqttClient: MQTTClient = MQTTClient(self)


    def loadConfig(self):
        self.config = self.config_handler.load_config()
        self.appConfig = self.config_handler.load_config_yaml()


    def updateNewConfig(self, config : Configuration):
        self.config_handler.save_config(config)
        self.restart()


    def start(self):
        #show platform
        self.logPlatform()        
        self.mqttClient.start()


    def restart(self):
        self.config = self.config_handler.load_config()
        self.mqttClient.stop()

    def exitApp(self):
        self.should_run = False
        self.mqttClient.stop()


    def shutdown(self):
        logger.info("🛑 Shutdown initiated...")
        if (not self.appConfig.app.disableShutdown):
            Tools.shutdown()
        else:
            logger.info("Shutdown disabled!")

    def reboot(self):
        logger.info("🔄 Reboot initiated...")
        if (not self.appConfig.app.disableShutdown):
            Tools.reboot()
        else:
            logger.info("Shutdown disabled!")                
    
    @staticmethod
    def logPlatform():
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
            logger.warning(f"Unknown system: {system}")
            sys.exit(1)