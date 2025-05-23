import json
import logging
import threading
import paho.mqtt.client as mqtt

from mqtt_presence.app_data import Configuration
from mqtt_presence.mqtt.mqtt_data import MqttTopic, MQTTHomeassistant, MQTTHomeassistantType


logger = logging.getLogger(__name__)


# Binary sensor for availability
AVAILABLE_SENSOR_TOPIC = "status"
AVAILABLE_STATUS_ONLINE = "online"
AVAILABLE_STATUS_OFFLINE = "offline"


class MQTTClient:
    def __init__(self, mqtt_callback):
        self._config: Configuration = None
        self._mqtt_callback = mqtt_callback
        self._client: str = None
        self._lock = threading.RLock()
        self.mqtt_topics: dict[str, MqttTopic] = {}


    def set_topics(self, topics: dict[str, MqttTopic]):
        self.mqtt_topics.clear()
        self.mqtt_topics[AVAILABLE_SENSOR_TOPIC] = MqttTopic("Online state", data=AVAILABLE_STATUS_ONLINE, homeassistant=MQTTHomeassistant(type=MQTTHomeassistantType.BINARY_SENSOR))
        self._publish_available(AVAILABLE_STATUS_ONLINE)
        self.mqtt_topics.update(topics)


    def handle_action(self, topic, function):
        publish_topic = f"{self._get_topic_prefix()}/{topic}/action"
        logger.info("🚀 Publish: %s: %s", publish_topic, function)
        self._client.publish(publish_topic, payload=function, retain=True)


    def publish_mqtt_data(self, data: dict[str, str], force: bool = False):
        with self._lock: 
            for topic, mqtt_topic in self.mqtt_topics.items():
                component = mqtt_topic.homeassistant.type if mqtt_topic.homeassistant else None
                if component==MQTTHomeassistantType.SENSOR or component==MQTTHomeassistantType.SWITCH or component==MQTTHomeassistantType.BINARY_SENSOR:
                    value = None
                    try:
                        value = data.get(topic)
                        old_value = mqtt_topic.data
                        if value is not None and (force or old_value is None or value != old_value):
                            mqtt_topic.data = value
                            topic = f"{self._get_topic_prefix()}/{topic}/state"
                            self._client.publish(topic, payload=str(value), retain=True)
                            logger.info("📡 Published %s: %s = %s",component.value, mqtt_topic.friendly_name, value)
                    except Exception as exception:      # pylint: disable=broad-exception-caught
                        logger.error("Failed to get %s data %s: %s  (%s, %s)", component.value, topic, exception, value, old_value)


    def connect(self, client_id, config: Configuration, password: str):
        self._config = config
        with self._lock:
            try:
                logger.info("🚪 Starting MQTT for %s on %s:%d",
                            client_id,
                            self._config.mqtt.broker.host,
                            self._config.mqtt.broker.port)
                self._create_client(client_id, password)
                self._client.connect(
                    self._config.mqtt.broker.host,
                    self._config.mqtt.broker.port,
                    self._config.mqtt.broker.keepalive
                )
                self._client.loop_start()
            except Exception: # pylint: disable=broad-exception-caught
                logger.exception("Connection failed")
                pass


    def is_connected(self):
        return False if self._client is None else self._client.is_connected()


    def disconnect(self):
        with self._lock:
            if self._client is not None:
                if self.is_connected():
                    logger.info("🚪 Stopping mqtt...")
                    self._publish_available("offline")
                self._client.loop_stop()
                self._client.disconnect()
                self.mqtt_topics.clear()
                self._client = None


    def _on_connect(self, _client, _userdata, _flags, reason_code, _properties=None):
        if self._client.is_connected():
            logger.info("🟢 Connected to MQTT broker")
            self._mqtt_callback("on_connect")
            #self._remove_old_discovery()  # TODO: Check seems not to work!
            self._subscribe_topics()
        else:
            if reason_code.value != 0:
                reason = reason_code.name if hasattr(reason_code, "name") else str(reason_code)
                logger.error("🔴 Connection to  MQTT broker failed: %s (rc=%s)", reason, reason_code.value if hasattr(reason_code, 'value') else reason_code)
            else:
                logger.info("🔴 Connection closed")


    def _on_disconnect(self, _client, _userdata, _flags, reason_code, _properties=None):
        reason = reason_code.name if hasattr(reason_code, "name") else str(reason_code)
        logger.error("🔴 Connection to  MQTT broker closed: %s (rc=%s)", reason, reason_code.value if hasattr(reason_code, 'value') else reason_code)
        self._mqtt_callback("on_disconnect")



    def _on_message(self, _client, _userdata, msg):
        payload = msg.payload.decode().strip().lower()
        logger.info("📩 Received command: %s → %s", msg.topic, payload)
        topic_prefix = self._get_topic_prefix()
        topic_without_prefix = msg.topic[len(topic_prefix)+1:] if msg.topic.startswith(topic_prefix) else topic_prefix

        for topic, mqtt_topic in self.mqtt_topics.items():
            component = mqtt_topic.homeassistant.type if mqtt_topic.homeassistant else None
            if component is not None and topic_without_prefix == f"{topic}/command":
                mqtt_topic.action(payload)



    def _get_topic_prefix(self):
        return f"{self._config.mqtt.broker.prefix}"


    def _get_available_topic(self):
        return f"{self._get_topic_prefix()}/{AVAILABLE_SENSOR_TOPIC}/state"



    def _subscribe_topics(self):
        for topic, mqtt_topic in self.mqtt_topics.items():
            component = mqtt_topic.homeassistant.type if mqtt_topic.homeassistant else None
            if component == MQTTHomeassistantType.BUTTON or component == MQTTHomeassistantType.SWITCH:
                self._client.subscribe(f"{self._get_topic_prefix()}/{topic}/command")


    def _publish_available(self, state):
        self._client.publish(self._get_available_topic(), payload=state, retain=True)
        logger.info("📡 Status publisched: %s", state)




    def _remove_old_discovery(self):
        discovery_prefix = self._config.mqtt.homeassistant.discovery_prefix
        node_id = self._config.mqtt.broker.prefix.replace("/", "_")

        for topic, mqtt_topic in self.mqtt_topics.items():
            component = mqtt_topic.homeassistant.type if mqtt_topic.homeassistant else None
            if (component is not None):
                topic = f"{discovery_prefix}/{component.value}/{node_id}/{topic}/config"
                self._client.publish(topic, payload="", retain=True)
                logger.info("🧹 Removed old discovery config: %s - %s", topic, mqtt_topic.friendly_name)


    def _add_dynamic_payload(self, payload, mqtt_topic: MqttTopic):
        if mqtt_topic.homeassistant.icon is not None:
            payload["icon"] = f"mdi:{mqtt_topic.homeassistant.icon}"
        if mqtt_topic.homeassistant.unit is not None:
            payload["unit_of_measurement"] = mqtt_topic.homeassistant.unit


    def _get_discovery_payload(self, raw_topic, mqtt_topic: MqttTopic, component, node_id):
        topic = f"{self._get_topic_prefix()}/{raw_topic}"

        device_info = {
            "identifiers": [node_id],
            "name": self._config.mqtt.homeassistant.device_name,
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

        if component == "button":
            payload["command_topic"] = f"{topic}/command"
            payload["payload_press"] = "press"
        elif component == "switch":
            payload["state_topic"] = f"{topic}/state"
            payload["command_topic"] = f"{topic}/command"
            payload["payload_off"] = "OFF"
            payload["payload_on"] = "ON"
        elif component == "binary_sensor":
            payload["state_topic"] = f"{topic}/state"
            payload["payload_on"] = "online"
            payload["payload_off"] = "offline"
            payload["device_class"] = "connectivity"
        elif component == "sensor":
            payload["state_topic"] = f"{topic}/state"
        elif component == "device_automation":
            payload["automation_type"] = "trigger"
            payload["topic"] = f"{topic}/action"
        return payload

    def publish_discovery(self):
        with self._lock:
            discovery_prefix = self._config.mqtt.homeassistant.discovery_prefix
            node_id = self._config.mqtt.broker.prefix.replace("/", "_")

            for topic, mqtt_topic in self.mqtt_topics.items():
                component = mqtt_topic.homeassistant.type if mqtt_topic.homeassistant else None
                if component is not None:
                    if mqtt_topic.homeassistant.actions is not None:
                        for action in mqtt_topic.homeassistant.actions:
                            discovery_topic = f"{discovery_prefix}/{component.value}/{node_id}/action_{topic}_{action}/config"
                            payload = self._get_discovery_payload(topic, mqtt_topic, component.value, node_id)
                            payload["type"] = action
                            payload["subtype"] = f"{topic}_{action}"
                            payload["unique_id"] = f"{payload['unique_id']}_{action}"
                            payload["payload"] = action
                            self._client.publish(discovery_topic, json.dumps(payload), retain=True)
                            logger.info("🧠 Action %s Discovery published for %s: %s", action, component.value, mqtt_topic.friendly_name)
                    else:
                        discovery_topic = f"{discovery_prefix}/{component.value}/{node_id}/{topic}/config"
                        payload = self._get_discovery_payload(topic, mqtt_topic, component.value, node_id)
                        self._client.publish(discovery_topic, json.dumps(payload), retain=True)
                        logger.info("🧠 Discovery published for %s: %s", component.value, mqtt_topic.friendly_name)


    def _create_client(self, client_id, password: str):
        with self._lock:
            if self._client is not None:
                self.disconnect()
            self._client = mqtt.Client(client_id=client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

            # Callback-Methoden
            self._client.on_connect = self._on_connect
            self._client.on_message = self._on_message
            self._client.on_disconnect = self._on_disconnect
            # Authentifizierung
            self._client.username_pw_set(self._config.mqtt.broker.username, password)
            # "Last Will"
            self._client.will_set(self._get_available_topic(), payload="offline", retain=True)
