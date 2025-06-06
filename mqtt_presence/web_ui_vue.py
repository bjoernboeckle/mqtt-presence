import logging

from flask import Flask, request, render_template, jsonify
from waitress import serve

from mqtt_presence.utils import Tools
from mqtt_presence.config.config_handler import ConfigYamlHelper
from mqtt_presence.devices.device_data import DeviceKey

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
            return render_template("index_vue.html", **{
                "appName": self.mqtt_app.NAME.replace("-", " ").title(),
                "version": self.mqtt_app.VERSION,
                "description": self.mqtt_app.DESCRIPTION,
                "config": ConfigYamlHelper.dataclass_to_serializable(self.mqtt_app.config),
                "status": self.mqtt_app.get_status()
            })


        @self.app.route("/config")
        def get_config():
            return jsonify({
                    "config":ConfigYamlHelper.dataclass_to_serializable(self.mqtt_app.config)
                    })


        @self.app.route("/status")
        def status():
            return jsonify({"status": self.mqtt_app.get_status()}), 200




        @self.app.route('/device/command', methods=['POST'])
        def device_command():
            data = request.json
            device_key: DeviceKey = data.get('device_key')
            data_key = data.get('data_key')
            function = data.get('function')
            logger.info("✏️  Web Device command: %s %s - %s", device_key, data_key, function)
            self.mqtt_app.devices.handle_command(device_key, data_key, function)
            return '', 204



        @self.app.route('/config/save', methods=['POST'])
        def update_config():
            data = request.json
            new_config = ConfigYamlHelper.convert_to_config(data.get('config'))
            new_password = data.get('password')
            logger.info("⚙️  Configuration updated....")
            self.mqtt_app.update_new_config(new_config, None if Tools.is_none_or_empty(new_password) else new_password)
            return jsonify({"message": "⚙️  Configuration updated!"}), 200
