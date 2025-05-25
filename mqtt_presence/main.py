import signal
import logging

from mqtt_presence.mqtt_presence_app import MQTTPresenceApp #, MQTTPresenceAppSingleton
from mqtt_presence.utils import Tools
from mqtt_presence.web_ui import WebUI

from mqtt_presence.parser import get_parser
from mqtt_presence.version import NAME

# setup logging
logger = logging.getLogger(__name__)


def main():
    def stop(_signum, _frame):
        logger.info("🚪 Stop signal recived, exiting...")
        if mqtt_app is not None:
            mqtt_app.stop()
        if user_interface is not None:
            user_interface.stop()
        Tools.exit_application()

    # Parse arguments
    args = get_parser(NAME).parse_args()

    # set log directory
    Tools.setup_logger(NAME, args.log)

    user_interface = None
    mqtt_app: MQTTPresenceApp = MQTTPresenceApp(args.config)

    start_up_msg = f"🚀 mqtt-presence startup (Version: {mqtt_app.VERSION})"
    logger.info("\n\n")
    logger.info(start_up_msg)

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    mqtt_app.start()

    #logger.info("ℹ️  Selected user_interface: %s", args.ui)
    WebUI(mqtt_app).run_ui()


if __name__ == "__main__":
    main()
