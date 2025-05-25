import logging
import threading

from mqtt_presence.mqtt.mqtt_client import MQTTClient
from mqtt_presence.devices.devices import Devices
from mqtt_presence.config.config_handler import ConfigHandler
from mqtt_presence.config.configuration import Configuration
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
        self._config_handler = ConfigHandler(data_path)
        self._should_run = True
        self._sleep_event = threading.Event()
        # load config
        self.config : Configuration = self._config_handler.load_config()
        self._thread = None
        self._mqtt_client: MQTTClient = MQTTClient(self._mqtt_callback)
        self._devices = Devices()


    def get_config_handler(self):
        return self._config_handler

    def get_mqtt_client(self):
        return self._mqtt_client

    def get_devices(self):
        return self._devices

    def update_new_config(self, config : Configuration, password: str = None):
        self._config_handler.save_config(config, password)
        self.restart()


    def start(self):
        #show platform
        Tools.log_platform()
        self.config = self._config_handler.load_config()
        self._devices.init(self.config, self._action_callback)
        self._should_run = True
        self._thread = threading.Thread(target=self._run_app_loop, daemon=True)
        self._thread.start()


    def restart(self):
        logger.info("🔄 ReStarting...")
        self.stop()
        self.start()



    def stop(self):
        self._should_run = False
        self._sleep_event.set()
        self._thread.join()
        self._thread = None
        self._mqtt_client.disconnect()
        self._devices.exit()



    def _on_connect(self):
        device_topics = self._devices.create_topics()
        self._devices.update_data()
        self._mqtt_client.set_topics(device_topics)
        self._mqtt_client.publish_mqtt_data(self._devices.data, True)
        if self.config.mqtt.homeassistant.enabled:
            self._mqtt_client.publish_discovery()


    def _action_callback(self, topic: str, function: str):
        logger.info("🚪 Callback: %s: %s", topic, function)
        if topic is not None:
            self._mqtt_client.handle_action(topic, function)
        self._sleep_event.set()


    def _mqtt_callback(self, function: str):
        if function == "on_connect":
            self._on_connect()
        elif function == "on_disconnect":
            pass


    def _run_app_loop(self):
        should_cleanup: bool = False
        while self._should_run:
            # handle mqtt (auto)connection
            if not self._mqtt_client.is_connected():
                should_cleanup = self.config.mqtt.homeassistant and  self.config.mqtt.homeassistant.enableAutoCleanup
                password = self._config_handler.get_password()
                self._mqtt_client.connect(self.config, password)
            else:
                if should_cleanup:
                    self._mqtt_client.clean_discovery_topics(False)
                    should_cleanup = False
                self._devices.update_data()
                self._mqtt_client.publish_mqtt_data(self._devices.data)

            self._sleep_event.clear()                                   # Reset the event for the next cycle
            self._sleep_event.wait(timeout=self.config.updateRate)      # Wait for the next update cycle
        logger.info("🔴 App main loop stopped")
