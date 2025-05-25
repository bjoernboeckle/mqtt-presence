import logging
import requests


from flask import Flask, request, render_template, jsonify
from waitress import serve

from mqtt_presence.utils import Tools
from mqtt_presence.config.configuration import Configuration
from mqtt_presence.config.config_handler import ConfigYamlHelper
from mqtt_presence.devices.raspberrypi.raspberrypi_data import GpioMode, GpioButton_Function

logger = logging.getLogger(__name__)

class WebUI:

    def __init__(self, mqtt_app):
        template_folder = Tools.resource_path("templates")
        self.app = Flask(__name__, template_folder=template_folder)
        self.mqtt_app = mqtt_app
        self.setup_routes()


    def stop(self):
        pass



    def is_server_running(self):
        try:

            response = requests.get(f"http://localhost:{self.mqtt_app.config.webServer.port}/health", timeout=2)
            if response.status_code == 200:
                return True
        except requests.ConnectionError:
            return False
        return False



    def run_ui(self):
        # use waitress or flask self run
        logging.info("Starting web ui at %s:%s", self.mqtt_app.config.webServer.host, self.mqtt_app.config.webServer.port)
        if Tools.is_debugger_active():
            self.app.run(host=self.mqtt_app.config.webServer.host, port=self.mqtt_app.config.webServer.port)
        else:
            serve(self.app, host=self.mqtt_app.config.webServer.host, port=self.mqtt_app.config.webServer.port)




    def setup_routes(self):

        @self.app.route("/")
        def index():
            return render_template("index.html", **{
                "appName": self.mqtt_app.NAME.replace("-", " ").title(),
                "version": self.mqtt_app.VERSION,
                "description": self.mqtt_app.DESCRIPTION})


        @self.app.route("/health")
        def health():
            return jsonify({"status": "running"}), 200

        @self.app.route('/config', methods=['GET'])
        def get_config():
            return jsonify(ConfigYamlHelper.dataclass_to_serializable(self.mqtt_app.config))

        @self.app.route('/gpio_modes', methods=['GET'])
        def get_gpio_modes():
            return jsonify([mode.value for mode in GpioMode])

        @self.app.route('/gpio_functions', methods=['GET'])
        def get_gpio_functions():
            return jsonify([func.value for func in GpioButton_Function])

        @self.app.route('/config', methods=['POST'])
        def update_config():
            data = request.json
            new_config: Configuration = ConfigYamlHelper.deserialize_enum(data.get('config'))
            new_password = data.get('password')
            logger.info("⚙️  Configuration updated....")
            self.mqtt_app.update_new_config(new_config, None if Tools.is_none_or_empty(new_password) else new_password)
            return jsonify({"message": "⚙️  Configuration updated!"}), 200

        @self.app.route("/status")
        def status():

            return jsonify({
                "mqtt_status": "🟢 Online" if self.mqtt_app.get_mqtt_client().is_connected() else "🔴 Offline",
                "raspberry_pi_status": "🟢 Online" if self.mqtt_app.get_devices().devices["raspberry"].online else "🔴 Offline",
                #"web_status":  "🟢 Online" if self.is_server_running() else "🔴 Offline",
                "devices_data": self.mqtt_app.get_devices().data
            })
