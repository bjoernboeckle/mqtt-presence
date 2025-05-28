import logging
import requests


from flask import Flask, request, render_template, jsonify
from waitress import serve

from mqtt_presence.utils import Tools
from mqtt_presence.config.configuration import Configuration
from mqtt_presence.config.config_handler import ConfigYamlHelper
from mqtt_presence.devices.device_data import DeviceData

logger = logging.getLogger(__name__)


class WebUIVue:

    def __init__(self, mqtt_app):
        template_folder = Tools.resource_path("templates")
        static_folder = Tools.resource_path("static")
        self.app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
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
            config: Configuration = self.mqtt_app.config
            devices_data = ConfigYamlHelper.dataclass_to_serializable(self.mqtt_app.devices.get_devices_data())
            return render_template("index_vue.html", **{
                "appName": self.mqtt_app.NAME.replace("-", " ").title(),
                "version": self.mqtt_app.VERSION,
                "description": self.mqtt_app.DESCRIPTION,
                "config": ConfigYamlHelper.dataclass_to_serializable(config),
                "mqtt_status": self.mqtt_app.mqtt_client.is_connected(),
                "raspberryPi_status": self.mqtt_app.devices.devices["raspberrypi"].online,
                "devices_data": devices_data})


        @self.app.route("/config")
        def get_config():
            config: Configuration = self.mqtt_app.config
            return jsonify(ConfigYamlHelper.dataclass_to_serializable(config))


        @self.app.route("/status")
        def status():
            devices_data = ConfigYamlHelper.dataclass_to_serializable(self.mqtt_app.devices.get_devices_data())
            return jsonify({
                "mqtt_status": self.mqtt_app.mqtt_client.is_connected(),
                "raspberryPi_status": self.mqtt_app.devices.devices["raspberrypi"].online,
                "devices_data": devices_data
            })


        @self.app.route("/health")
        def health():
            return jsonify({"status": "running"}), 200



        @self.app.route('/pcutils/command', methods=['POST'])
        def pcutils_command():
            pcutils_data: dict[str, DeviceData] = self.mqtt_app.devices.pc_utils.data
            data = request.json
            for key, device_data in pcutils_data.items():
                if key == data.get('function'):
                    if device_data.action is not None:
                        device_data.action("")
            return '', 204





        @self.app.route('/config/save', methods=['POST'])
        def update_config():
            data = request.json
            new_config: Configuration = ConfigYamlHelper.deserialize_enum(data.get('config'))
            new_password = data.get('password')
            logger.info("⚙️  Configuration updated....")
            self.mqtt_app.update_new_config(new_config, None if Tools.is_none_or_empty(new_password) else new_password)
            return jsonify({"message": "⚙️  Configuration updated!"}), 200
