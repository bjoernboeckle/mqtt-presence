import threading
import time
import json
import logging

import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


class MqttCommand:
    def __init__(self, friendly_name, action):
        self.friendly_name = friendly_name
        self.action = action


class MQTTClient:
    # Binary sensor dictonary
    STATUS_BINARY_SENSOR = "status"

    def __init__(self, mqtt_app):
        self.mqtt_app = mqtt_app
        self.client = None
        self.lock = threading.RLock()
        self.thread = threading.Thread(target=self._run_mqtt_loop, daemon=True)

        # MQTT binary_sensors
        self.__binary_sensors__ = {
            self.STATUS_BINARY_SENSOR: MqttCommand("Online state", None),
        }

        # MQTT buttons
        self.__buttons__ = {
            "shutdown": MqttCommand("Shutdown pc", self.mqtt_app.shutdown),
            "reboot": MqttCommand("Reboot pc", self.mqtt_app.reboot),
        }


    def start(self):
        self.thread.start()

    def _run_mqtt_loop(self):
        try:
            while self.mqtt_app.should_run:
                # mqtt starten
                if not self.is_connected():
                    self.connect()
                time.sleep(5)
        finally:
            self.stop()


    def config(self):
        return self.mqtt_app.config


    def is_connected(self):
        return False if self.client is None else self.client.is_connected()



    def on_connect(self, client, userdata, flags, rc, properties=None):  # pylint: disable=too-many-positional-arguments disable=unused-argument
        if self.client.is_connected():
            logger.info("🟢 Connected to MQTT broker")
            self.publish_status("online")
            self.subscribe_topics()
            self.remove_old_discovery()
            if self.config().mqtt.homeassistant.enabled:
                self.publish_discovery()
        else:
            if rc.value != 0:
                reason = rc.name if hasattr(rc, "name") else str(rc)
                logger.error("🔴 Connection to  MQTT broker failed: %s (rc=%s)", reason, rc.value if hasattr(rc, 'value') else rc)
            else:
                logger.info("🔴 Connection closed")


    def on_disconnect(self, client, userdata, flags, rc, properties=None): # pylint: disable=too-many-positional-arguments disable=unused-argument
        reason = rc.name if hasattr(rc, "name") else str(rc)
        logger.error("🔴 Connection to  MQTT broker closed: %s (rc=%s)", reason, rc.value if hasattr(rc, 'value') else rc)


    def on_message(self, client, userdata, msg):  # pylint: disable=too-many-positional-arguments disable=unused-argument
        payload = msg.payload.decode().strip().lower()
        logger.info("📩 Received command: %s → %s", msg.topic, payload)

        topic = self.get_topic()
        topic_without_prefix = msg.topic[len(topic)+1:] if msg.topic.startswith(topic) else topic

        for button, mqtt_cmd in self.__buttons__.items():
            if topic_without_prefix == button:
                mqtt_cmd.action()



    def get_topic(self):
        return f"{self.mqtt_app.config.mqtt.broker.prefix}"


    def get_status_topic(self):
        return f"{self.get_topic()}/{self.STATUS_BINARY_SENSOR}"



    def subscribe_topics(self):
        for button in self.__buttons__:
            self.client.subscribe(f"{self.get_topic()}/{button}")


    def publish_status(self, state):
        self.client.publish(self.get_status_topic(), payload=state, retain=True)
        logger.info("📡 Status publisched: %s", state)



    def remove_old_discovery(self):
        discovery_prefix = self.config().mqtt.homeassistant.discovery_prefix
        node_id = self.mqtt_app.config.mqtt.broker.prefix.replace("/", "_")


        for comp, keys in [
            ("button", self.__buttons__),
            ("binary_sensor", self.__binary_sensors__)
        ]:
            for command in keys:
                topic = f"{discovery_prefix}/{comp}/{node_id}/{command}/config"
                self.client.publish(topic, payload="", retain=True)
                logger.info("🧹 Removed old discovery config: %s", topic)


    def publish_discovery(self):
        discovery_prefix = self.config().mqtt.homeassistant.discovery_prefix
        node_id = self.mqtt_app.config.mqtt.broker.prefix.replace("/", "_")

        device_info = {
            "identifiers": [node_id],
            "name": self.config().mqtt.homeassistant.device_name,
            "manufacturer": "mqtt-presence",
            "model": "Presence Agent"
        }

        # MQTT-Buttons für Shutdown und Reboot
        for button, mqtt_cmd in self.__buttons__.items():
            #topic = command_topic
            topic = f"{self.get_topic()}/{button}"
            discovery_topic = f"{discovery_prefix}/button/{node_id}/{button}/config"
            payload = {
                "name": mqtt_cmd.friendly_name,
                "command_topic": topic,
                "payload_press": "press",
                "availability_topic": self.get_status_topic(),
                "payload_available": "online",
                "payload_not_available": "offline",
                "unique_id": f"{node_id}_{button}",
                "device": device_info
            }
            self.client.publish(discovery_topic, json.dumps(payload), retain=True)
            logger.info("🧠 Discovery published for button: %s", mqtt_cmd.friendly_name)

        # MQTT binary sensors
        for binary_sensor, mqtt_cmd in self.__binary_sensors__.items():
            topic = f"{self.get_topic()}/{binary_sensor}"
            discovery_topic = f"{discovery_prefix}/binary_sensor/{node_id}/{binary_sensor}/config"
            payload = {
                "name": mqtt_cmd.friendly_name,
                "state_topic": topic,
                "payload_on": "online",
                "payload_off": "offline",
                "availability_topic": self.get_status_topic(),
                "payload_available": "online",
                "payload_not_available": "offline",
                "device_class": "connectivity",
                "unique_id": f"{node_id}_status",
                "device": device_info
            }
            self.client.publish(discovery_topic, json.dumps(payload), retain=True)
            logger.info("🧠 Discovery published for binary sensor %s", mqtt_cmd.friendly_name)


    def create_client(self):
        with self.lock:
            if self.client is not None:
                self.stop()
            self.client = mqtt.Client(client_id=self.mqtt_app.app_config.app.mqtt.client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

            # Callback-Methoden
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.on_disconnect = self.on_disconnect
            # Authentifizierung
            password = self.mqtt_app.config_handler.get_decrypt_password(self.mqtt_app.config.mqtt.broker.encrypted_password)
            self.client.username_pw_set(self.config().mqtt.broker.username, password)
            # "Last Will"
            self.client.will_set(self.get_status_topic(), payload="offline", retain=True)

    def connect(self):
        with self.lock:
            try:
                logger.info("🚪 Starting MQTT for %s on %s:%d",
                            self.mqtt_app.app_config.app.mqtt.client_id,
                            self.config().mqtt.broker.host,
                            self.config().mqtt.broker.port)
                self.create_client()
                self.client.connect(
                    self.config().mqtt.broker.host,
                    self.config().mqtt.broker.port,
                    self.config().mqtt.broker.keepalive
                )
                self.client.loop_start()
            except Exception: # pylint: disable=broad-exception-caught
                logger.exception("Connection failed")


    def stop(self):
        with self.lock:
            if self.client is not None:
                if self.is_connected():
                    logger.info("🚪 Stopping mqtt...")
                    self.publish_status("offline")
                self.client.loop_stop()
                self.client.disconnect()
                self.client = None
