from mqtt_presence.app_data import Configuration
from mqtt_presence.utils import Tools

from waitress import serve
from flask import Flask, request, render_template, jsonify
import copy
import logging
logger = logging.getLogger(__name__)


class WebUI:

    def __init__(self, appState):
        template_folder = Tools.resource_path("templates")
        self.app = Flask(__name__, template_folder=template_folder)
        self.appState = appState
        self.setup_routes()


    def stop(self):
        pass


    def runUI(self):
        # use waitress or flask self run
        if Tools.is_debugger_active():
            self.app.run(host=self.appState.appConfig.app.webServer.host, port=self.appState.appConfig.app.webServer.port)
        else:
            serve(self.app, host=self.appState.appConfig.app.webServer.host, port=self.appState.appConfig.app.webServer.port)



    def setup_routes(self):
        @self.app.route("/", methods=["GET", "POST"])
        def index():
            if request.method == "POST":
                new_config: Configuration = copy.deepcopy(self.appState.config)
                # raspberry pi
                #new_config.raspi
                #new_config["enable_raspberrypi"] = request.form.get("enable_raspberrypi", "off") == "on"  # ergibt True oder False
                #gpioLed = request.form.get("gpio_led")
                #if (gpioLed is not None): new_config["gpio_led"] = int(gpioLed)
                #gpio_button = request.form.get("gpio_button", None)
                #if (gpio_button is not None): new_config["gpio_button"] = int(gpio_button)
                
                # mqtt broker
                new_config.mqtt.broker.host = request.form.get("host")
                new_config.mqtt.broker.username = request.form.get("username")
                password = request.form.get("password")
                if password:
                    #new_config.mqtt.broker.password = request.form.get("password")
                    new_config.mqtt.broker.encrypted_password =  self.appState.config_handler.get_encrypt_password(password)
                new_config.mqtt.broker.prefix = Tools.sanitize_mqtt_topic(request.form.get("prefix"))
                
                #homeassistant
                new_config.mqtt.homeassistant.enabled = request.form.get("enable_HomeAssistant", "off") == "on"  #  True or False
                new_config.mqtt.homeassistant.device_name = request.form.get("device_name", self.appState.config.mqtt.homeassistant.device_name)
                new_config.mqtt.homeassistant.discovery_prefix = request.form.get("discovery_prefix", self.appState.config.mqtt.homeassistant.discovery_prefix)
                logger.info("⚙️ Konfiguration aktualisiert....")
                self.appState.updateNewConfig(new_config)
                self.appState.restart();

            return render_template("index.html", **{
                #MQTT
                "host": self.appState.config.mqtt.broker.host,
                "username": self.appState.config.mqtt.broker.username,
                "prefix": self.appState.config.mqtt.broker.prefix,

                #Homeassistant
                "enable_HomeAssistant": self.appState.config.mqtt.homeassistant.enabled,
                "discovery_prefix": self.appState.config.mqtt.homeassistant.discovery_prefix,
                "device_name": self.appState.config.mqtt.homeassistant.device_name,
                #raspberrypi
                #"enable_raspberrypi": self.config_handler.config.get("enable_raspberrypi"),
                #"gpio_led":  int(self.config_handler.config.get("gpio_led")),
                #"gpio_button": int(self.config_handler.config.get("gpio_button"))
            })


        @self.app.route("/status")
        def status():
            return jsonify({
                "mqtt_status": "Online" if self.appState.mqttClient.is_connected() else "Offline",
                "client_id": self.appState.appConfig.app.mqtt.client_id,
                #"raspberrypi_extension_status": self.helpers.appstate.raspberrypi.status.replace('"', '')
            })


            