import copy
import logging

from flask import Flask, request, render_template, jsonify
from waitress import serve

from mqtt_presence.utils import Tools
from mqtt_presence.app_data import Configuration

logger = logging.getLogger(__name__)

class WebUI:

    def __init__(self, mqtt_app):
        template_folder = Tools.resource_path("templates")
        self.app = Flask(__name__, template_folder=template_folder)
        self.mqtt_app = mqtt_app
        self.setup_routes()


    def stop(self):
        pass


    def run_ui(self):
        # use waitress or flask self run
        if Tools.is_debugger_active():
            self.app.run(host=self.mqtt_app.app_config.app.webServer.host, port=self.mqtt_app.app_config.app.webServer.port)
        else:
            serve(self.app, host=self.mqtt_app.app_config.app.webServer.host, port=self.mqtt_app.app_config.app.webServer.port)



    def setup_routes(self):
        @self.app.route("/", methods=["GET", "POST"])
        def index():
            if request.method == "POST":
                new_config: Configuration = copy.deepcopy(self.mqtt_app.config)
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
                    new_config.mqtt.broker.encrypted_password =  self.mqtt_app.config_handler.get_encrypt_password(password)
                new_config.mqtt.broker.prefix = Tools.sanitize_mqtt_topic(request.form.get("prefix"))

                #homeassistant
                new_config.mqtt.homeassistant.enabled = request.form.get("enable_HomeAssistant", "off") == "on"  #  True or False
                new_config.mqtt.homeassistant.device_name = request.form.get("device_name", self.mqtt_app.config.mqtt.homeassistant.device_name)
                new_config.mqtt.homeassistant.discovery_prefix = request.form.get("discovery_prefix", self.mqtt_app.config.mqtt.homeassistant.discovery_prefix)
                logger.info("⚙️ Konfiguration aktualisiert....")
                self.mqtt_app.update_new_config(new_config)
                self.mqtt_app.restart()

            return render_template("index.html", **{
                "appName": Tools.APP_NAME.replace("-", " ").title(),
                "version": self.mqtt_app.version,
                #MQTT
                "host": self.mqtt_app.config.mqtt.broker.host,
                "username": self.mqtt_app.config.mqtt.broker.username,
                "prefix": self.mqtt_app.config.mqtt.broker.prefix,

                #Homeassistant
                "enable_HomeAssistant": self.mqtt_app.config.mqtt.homeassistant.enabled,
                "discovery_prefix": self.mqtt_app.config.mqtt.homeassistant.discovery_prefix,
                "device_name": self.mqtt_app.config.mqtt.homeassistant.device_name,
                #raspberrypi
                #"enable_raspberrypi": self.config_handler.config.get("enable_raspberrypi"),
                #"gpio_led":  int(self.config_handler.config.get("gpio_led")),
                #"gpio_button": int(self.config_handler.config.get("gpio_button"))
            })


        @self.app.route("/status")
        def status():
            return jsonify({
                "mqtt_status": "Online" if self.mqtt_app.mqtt_client.is_connected() else "Offline",
                "client_id": self.mqtt_app.app_config.app.mqtt.client_id,
                #"raspberrypi_extension_status": self.helpers.appstate.raspberrypi.status.replace('"', '')
            })


        @self.app.route('/shutdown', methods=['POST'])
        def shutdown():
            #self.mqtt_app.shutdwon()
            logger.info("shutdwon....")
            return '', 204

        @self.app.route('/restart', methods=['POST'])
        def restart():
            #self.mqtt_app.reboot()
            logger.info("reboot....")
            return '', 204
