import threading
import time
import json
import logging

import paho.mqtt.client as mqtt

from mqtt_presence.mqtt_topics import MqttTopics, MqttTopic

logger = logging.getLogger(__name__)


# Binary sensor for availability
AVAILABLE_SENSOR = "status"

class MQTTClient:
    def __init__(self, mqtt_app):
        self.mqtt_app = mqtt_app
        self.client = None
        self.lock = threading.RLock()
        self.thread = threading.Thread(target=self._run_mqtt_loop, daemon=True)

        self.mqtt_topics = MqttTopics()



    def _run_mqtt_loop(self):
        try:
            while self.mqtt_app.should_run:
                # mqtt starten
                if not self.is_connected():
                    self._connect()
                else:
                    self.mqtt_topics.update_data()
                    self._publish_mqtt_data()
                time.sleep(5)
        finally:
            self.disconnect()


    def _config(self):
        return self.mqtt_app.config




    def _on_connect(self, _client, _userdata, _flags, reason_code, _properties=None):
        if self.client.is_connected():
            logger.info("🟢 Connected to MQTT broker")
            #self._remove_old_discovery()  # TODO: Check seems not to work!
            self._publish_available("online")
            self._publish_mqtt_data(True)
            self._subscribe_topics()
            if self._config().mqtt.homeassistant.enabled:
                self._publish_discovery()
        else:
            if reason_code.value != 0:
                reason = reason_code.name if hasattr(reason_code, "name") else str(reason_code)
                logger.error("🔴 Connection to  MQTT broker failed: %s (rc=%s)", reason, reason_code.value if hasattr(reason_code, 'value') else reason_code)
            else:
                logger.info("🔴 Connection closed")


    def _on_disconnect(self, _client, _userdata, _flags, reason_code, _properties=None):
        reason = reason_code.name if hasattr(reason_code, "name") else str(reason_code)
        logger.error("🔴 Connection to  MQTT broker closed: %s (rc=%s)", reason, reason_code.value if hasattr(reason_code, 'value') else reason_code)


    def _on_message(self, _client, _userdata, msg):
        payload = msg.payload.decode().strip().lower()
        logger.info("📩 Received command: %s → %s", msg.topic, payload)

        topic = self._get_topic()
        topic_without_prefix = msg.topic[len(topic)+1:] if msg.topic.startswith(topic) else topic

        for button, mqtt_topic in self.mqtt_topics.buttons.items():
            if topic_without_prefix == button:
                mqtt_topic.action()



    def _get_topic(self):
        return f"{self.mqtt_app.config.mqtt.broker.prefix}"


    def _get_available_topic(self):
        return f"{self._get_topic()}/{AVAILABLE_SENSOR}"



    def _subscribe_topics(self):
        for button in self.mqtt_topics.buttons:
            self.client.subscribe(f"{self._get_topic()}/{button}")


    def _publish_available(self, state):
        self.mqtt_topics.binary_sensors_dats[AVAILABLE_SENSOR] = state
        self.client.publish(self._get_available_topic(), payload=state, retain=True)
        logger.info("📡 Status publisched: %s", state)



    def _publish_mqtt_data(self, force: bool = False):
        for component, topics in self.mqtt_topics.get_topics_by_group().items():
            if component=="sensor":
                for topic, mqtt_topic in topics.items():
                    value = None
                    try:
                        value = self.mqtt_topics.sensors_data[topic]
                        old_value =  self.mqtt_topics.sensors_data_old[topic]
                    except Exception as exception:      # pylint: disable=broad-exception-caught
                        logger.error("Failed to get sensor data %s: %s", topic, exception)
                    if value is not None and (value != old_value or force):
                        self.mqtt_topics.sensors_data[topic] = value
                        self.mqtt_topics.sensors_data_old[topic] = value
                        topic = f"{self._get_topic()}/{topic}"
                        self.client.publish(topic, payload=str(value), retain=True)
                        logger.info("📡 Published sensor: %s = %s", mqtt_topic.friendly_name, value)



    def _remove_old_discovery(self):
        discovery_prefix = self._config().mqtt.homeassistant.discovery_prefix
        node_id = self.mqtt_app.config.mqtt.broker.prefix.replace("/", "_")

        for component, topics in self.mqtt_topics.get_topics_by_group().items():
            for topic, mqtt_topic in topics.items():
                topic = f"{discovery_prefix}/{component}/{node_id}/{topic}/config"
                self.client.publish(topic, payload="", retain=True)
                logger.info("🧹 Removed old discovery config: %s - %s", topic, mqtt_topic.friendly_name)


    def _add_dynamic_payload(self, payload, mqtt_topic: MqttTopic):
        if mqtt_topic.icon is not None:
            payload["icon"] = f"mdi:{mqtt_topic.icon}"
        if mqtt_topic.unit is not None:
            payload["unit_of_measurement"] = mqtt_topic.unit


    def _get_discovery_payload(self, topic, mqtt_topic: MqttTopic, component, node_id):
        topic = f"{self._get_topic()}/{topic}"

        device_info = {
            "identifiers": [node_id],
            "name": self._config().mqtt.homeassistant.device_name,
            "manufacturer": "mqtt-presence",
            "model": "Presence Agent"
        }
        payload = {
                "name": mqtt_topic.friendly_name,
                "availability_topic": self._get_available_topic(),
                "payload_available": "online",
                "payload_not_available": "offline",
                "unique_id": f"{node_id}_{topic}",
                "device": device_info
        }
        self._add_dynamic_payload(payload, mqtt_topic)

        if component=="button":
            payload["command_topic"] = topic
            payload["payload_press"] = "press"
        elif component=="binary_sensor":
            payload["state_topic"] = topic
            payload["payload_on"] = "online"
            payload["payload_off"] = "offline"
            payload["device_class"] = "connectivity"
        elif component=="sensor":
            payload["state_topic"] = topic
        return payload

    def _publish_discovery(self):
        discovery_prefix = self._config().mqtt.homeassistant.discovery_prefix
        node_id = self.mqtt_app.config.mqtt.broker.prefix.replace("/", "_")

        for component, topics in self.mqtt_topics.get_topics_by_group().items():
            for topic, mqtt_topic in topics.items():
                discovery_topic = f"{discovery_prefix}/{component}/{node_id}/{topic}/config"
                payload = self._get_discovery_payload(topic, mqtt_topic, component, node_id)
                self.client.publish(discovery_topic, json.dumps(payload), retain=True)
                logger.info("🧠 Discovery published for %s: %s", component, mqtt_topic.friendly_name)


    def _create_client(self):
        with self.lock:
            if self.client is not None:
                self.disconnect()
            self.client = mqtt.Client(client_id=self.mqtt_app.app_config.app.mqtt.client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

            # Callback-Methoden
            self.client.on_connect = self._on_connect
            self.client.on_message = self._on_message
            self.client.on_disconnect = self._on_disconnect
            # Authentifizierung
            password = self.mqtt_app.config_handler.get_decrypt_password(self.mqtt_app.config.mqtt.broker.encrypted_password)
            self.client.username_pw_set(self._config().mqtt.broker.username, password)
            # "Last Will"
            self.client.will_set(self._get_available_topic(), payload="offline", retain=True)


    def _connect(self):
        with self.lock:
            try:
                logger.info("🚪 Starting MQTT for %s on %s:%d",
                            self.mqtt_app.app_config.app.mqtt.client_id,
                            self._config().mqtt.broker.host,
                            self._config().mqtt.broker.port)
                self._create_client()
                self.client.connect(
                    self._config().mqtt.broker.host,
                    self._config().mqtt.broker.port,
                    self._config().mqtt.broker.keepalive
                )
                self.client.loop_start()
            except Exception: # pylint: disable=broad-exception-caught
                logger.exception("Connection failed")


    def is_connected(self):
        return False if self.client is None else self.client.is_connected()


    def disconnect(self):
        with self.lock:
            if self.client is not None:
                if self.is_connected():
                    logger.info("🚪 Stopping mqtt...")
                    self._publish_available("offline")
                self.client.loop_stop()
                self.client.disconnect()
                self.client = None


    def start_mqtt(self):
        self.thread.start()
