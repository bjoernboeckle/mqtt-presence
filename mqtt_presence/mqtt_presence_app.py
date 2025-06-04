import logging
import threading
from typing import Optional

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

    def __init__(self, data_path: Optional[str] = None):
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


    @property
    def config_handler(self) -> ConfigHandler:
        return self._config_handler

    @property
    def mqtt_client(self) -> MQTTClient:
        return self._mqtt_client

    @property
    def devices(self) -> Devices:
        return self._devices

    def force_update(self):
        logger.info("Force Update called")
        self._sleep_event.set()

    def update_new_config(self, new_config : Configuration, password: Optional[str] = None):
        if new_config.mqtt.broker.prefix != self.config.mqtt.broker.prefix and self.mqtt_client.is_connected():
            # try to remove topics, since prefix was changed
            self.stop(True)
            self.mqtt_client.remove_topics()
            self.mqtt_client.disconnect(True)
            sleep_event = threading.Event()
            sleep_event.wait(4)
        else:
            self.stop()

        logger.info("🔄 ReStarting...")
        self._config_handler.save_config(new_config, password)
        self.start()


    def start(self):
        #show platform
        Tools.log_platform()
        self.config = self._config_handler.load_config()
        self._devices.init(self.config, self._device_callback)
        self._should_run = True
        self._thread = threading.Thread(target=self._run_app_loop, daemon=True)
        self._thread.start()




    def stop(self, keep_connected: bool = False):
        self._should_run = False
        self._sleep_event.set()
        if self._thread is not None:
            self._thread.join()
            self._thread = None
        if not keep_connected:
            self._mqtt_client.disconnect()
        self._devices.exit()


    def _on_connect(self):
        #device_topics = self._devices.create_topics()
        self._devices.update_data(mqtt_online = self._mqtt_client.is_connected())
        self._mqtt_client.set_devices_data(self._devices)
        self._mqtt_client.publish_mqtt_data(True)
        if self.config.mqtt.homeassistant.enabled:
            self._mqtt_client.publish_discovery()



    def _device_callback(self, device_key: Optional[str] = None, data_key: Optional[str] = None, function: Optional[str] = None):
        logger.info("🚪 Callback Device %s: %s: %s", device_key, data_key, function)
        if device_key is not None and data_key is not None and function is not None:
            self._mqtt_client.handle_action(device_key, data_key, function)
        self.force_update()



    def _mqtt_callback(self, function: str):
        if function == "on_connect":
            self._on_connect()
        elif function == "on_disconnect":
            pass
        elif function == "on_message_action":
            pass



    def _run_app_loop(self):
        should_cleanup: bool = False
        while self._should_run:
            self._sleep_event.clear()                                   # Reset the event for the next cycle
            self._devices.update_data(mqtt_online = self._mqtt_client.is_connected())
            if self.config.mqtt.enabled:
                # handle mqtt (auto)connection
                if not self._mqtt_client.is_connected():
                    should_cleanup = self.config.mqtt.homeassistant and self.config.mqtt.homeassistant.enableAutoCleanup
                    password = self._config_handler.get_password()
                    self._mqtt_client.connect(self.config, password)
                else:
                    if should_cleanup:
                        self._mqtt_client.clean_discovery_topics(False)
                        should_cleanup = False
                    self._mqtt_client.publish_mqtt_data()


            self._sleep_event.wait(timeout=self.config.updateRate)      # Wait for the next update cycle
        logger.info("🔴 App main loop stopped")
