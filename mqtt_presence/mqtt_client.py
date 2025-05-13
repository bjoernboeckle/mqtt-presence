import paho.mqtt.client as mqtt
import threading
import time
import json

import logging
logger = logging.getLogger(__name__)


class mqtt_command:
    def __init__(self, friendlyName, action):
        self.friendlyName = friendlyName
        self.action = action


class MQTTClient:
    # Binary sensor dictonary
    STATUS_BINARY_SENSOR = "status"

    def __init__(self, appState):
        self.appState = appState
        self.client = None
        self.lock = threading.RLock()
        self.thread = threading.Thread(target=self._run_mqtt_loop, daemon=True)

        # MQTT binary_sensors
        self.BINARY_SENSORS = {
            self.STATUS_BINARY_SENSOR: mqtt_command("Online state", None),
        }

        # MQTT buttons
        self.BUTTONS = {
            "shutdown": mqtt_command("Shutdown pc", self.appState.shutdown),
            "reboot": mqtt_command("Reboot pc", self.appState.reboot),
        }

       

    def start(self):
        self.thread.start()

    def _run_mqtt_loop(self):
        try:
            while self.appState.should_run:
                # mqtt starten
                if (not self.is_connected()):
                    self.start()
                time.sleep(5)
        finally:
            self.stop()        


    def config(self):
        return self.appState.config


    def is_connected(self):
        return False if (self.client is None) else self.client.is_connected()



    def on_connect(self, client, userdata, flags, rc, properties=None):
        if (self.client.is_connected()):
            logger.info("🟢 Connected to MQTT broker")
            self.publish_status("online")
            self.subscribe_topics()
            self.remove_old_discovery()
            if (self.config().mqtt.homeassistant.enabled): self.publish_discovery()
        else:
            if (rc.value != 0):
                reason = rc.name if hasattr(rc, "name") else str(rc)
                logger.error(f"🔴 Connection to  MQTT broker failed: {reason} (rc={rc.value if hasattr(rc, 'value') else rc})")
            else:
                logger.info("🔴 Connection closed")
                


    def on_disconnect(self, client, userdata, flags, rc, properties=None):
        reason = rc.name if hasattr(rc, "name") else str(rc)
        logger.error(f"🔴 Connection to  MQTT broker closed: {reason} (rc={rc.value if hasattr(rc, 'value') else rc})")        


    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode().strip().lower()
        logger.info(f"📩 Received command: {msg.topic} → {payload}")

        topic = self.getTopic()
        if msg.topic.startswith(topic):
            topic_without_prefix = msg.topic[len(topic)+1:]

        for button, mqttCmd in self.BUTTONS.items():
            if (topic_without_prefix == button):
                mqttCmd.action()



    def getTopic(self):    
        return f"{self.appState.config.mqtt.broker.prefix}"


    def get_status_topic(self):
        return f"{self.getTopic()}/{self.STATUS_BINARY_SENSOR}"



    def subscribe_topics(self):
        for button in self.BUTTONS:
            self.client.subscribe(f"{self.getTopic()}/{button}")
        

    def publish_status(self, state):
        self.client.publish(self.get_status_topic(), payload=state, retain=True)
        logger.info(f"📡 Status publisched: {state}")



    def remove_old_discovery(self):
        discovery_prefix = self.config().mqtt.homeassistant.discovery_prefix
        node_id = self.appState.config.mqtt.broker.prefix.replace("/", "_")
       

        for comp, keys in [
            ("button", self.BUTTONS),
            ("binary_sensor", self.BINARY_SENSORS)
        ]:
            for command in keys:
                topic = f"{discovery_prefix}/{comp}/{node_id}/{command}/config"
                self.client.publish(topic, payload="", retain=True)
                logger.info(f"🧹 Removed old discovery config: {topic}")


    def publish_discovery(self):
        discovery_prefix = self.config().mqtt.homeassistant.discovery_prefix
        node_id = self.appState.config.mqtt.broker.prefix.replace("/", "_")

        device_info = {
            "identifiers": [node_id],
            "name": self.config().mqtt.homeassistant.device_name,
            "manufacturer": "mqtt-presence",
            "model": "Presence Agent"
        }

        # MQTT-Buttons für Shutdown und Reboot
        for button, mqttCmd in self.BUTTONS.items():
            #topic = command_topic
            topic = f"{self.getTopic()}/{button}"
            discovery_topic = f"{discovery_prefix}/button/{node_id}/{button}/config"
            payload = {
                "name": mqttCmd.friendlyName,
                "command_topic": topic,
                "payload_press": "press",
                "availability_topic": self.get_status_topic(),
                "payload_available": "online",
                "payload_not_available": "offline",
                "unique_id": f"{node_id}_{button}",
                "device": device_info
            }
            self.client.publish(discovery_topic, json.dumps(payload), retain=True)
            logger.info(f"🧠 Discovery published for button: {mqttCmd.friendlyName}")

        # MQTT binary sensors
        for binary_sensor, mqttCmd in self.BINARY_SENSORS.items():
            topic = f"{self.getTopic()}/{binary_sensor}"
            discovery_topic = f"{discovery_prefix}/binary_sensor/{node_id}/{binary_sensor}/config"    
            payload = {
                "name": mqttCmd.friendlyName,
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
            logger.info(f"🧠 Discovery published for binary sensor {mqttCmd.friendlyName}")


    def createClient(self):
        with self.lock:
            if (self.client is not None): self.stop()
            self.client = mqtt.Client(client_id=self.appState.appConfig.app.mqtt.client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

            # Callback-Methoden
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.on_disconnect = self.on_disconnect
            # Authentifizierung
            password = self.appState.config_handler.get_decrypt_password(self.appState.config.mqtt.broker.encrypted_password)
            self.client.username_pw_set(self.config().mqtt.broker.username, password)
            # "Last Will"
            self.client.will_set(self.get_status_topic(), payload="offline", retain=True)

    def start(self):           
        with self.lock:
            try:
                logger.info(f"🚪 Starting MQTT for {self.appState.appConfig.app.mqtt.client_id} on {self.config().mqtt.broker.host}:{self.config().mqtt.broker.port}")
                self.createClient()
                self.client.connect(
                    self.config().mqtt.broker.host,
                    self.config().mqtt.broker.port, 
                    self.config().mqtt.broker.keepalive
                )
                self.client.loop_start()
            except Exception as e:
                logger.exception("Connection failed")


    def stop(self):
        with self.lock:        
            if (self.client is not None):
                logger.info("🚪 Stopping mqtt...")
                if (self.is_connected()):
                    self.publish_status("offline")
                self.client.loop_stop()
                self.client.disconnect()
                self.client = None
