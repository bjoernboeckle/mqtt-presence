import argparse
import signal
import sys
import logging

from mqtt_presence.mqtt_presence_app import MQTTPresenceApp#, MQTTPresenceAppSingleton
from mqtt_presence.utils import Tools
from mqtt_presence.web_ui import WebUI
from mqtt_presence.console_ui import ConsoleUI

# setup logging
logFile = Tools.get_log_path(Tools.APP_NAME, "mqtt_presence.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),  # Konsole
        logging.FileHandler(logFile, mode='a', encoding='utf-8')  # Datei (append mode)
    ]
)
logger = logging.getLogger(__name__)




# define Arguemnts
parser = argparse.ArgumentParser(description=Tools.APP_NAME)

 # Optional argument for selecting the UI
parser.add_argument(
    '--ui', 
    choices=['webUI', 'console'],  # Available options
    default='webUI',  # Default value
    type=str,  # Argument type
    help="Select the UI: 'webUI' (default), 'console'."
)

# Positional argument for selecting the UI (defaults to 'webUI')
#parser.add_argument('ui_positional',
#    nargs='?',  # Makes it optional
#    choices=['webUI', 'console', 'none'],
#    help="Select the UI (same as --ui option)."
#)


def main():
    def stop(_signum, _frame):
        logger.info("🚪 Stop signal recived, exiting...")
        if mqtt_app is not None:
            mqtt_app.exit_app()
        if ui is not None:
            ui.stop()
        Tools.exit_application()


    mqtt_app: MQTTPresenceApp = MQTTPresenceApp()
    ui = None

    start_up_msg = f"🚀 mqtt-presence startup (Version: {mqtt_app.version})"
    logger.info("\n\n")
    logger.info(start_up_msg)


    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    mqtt_app.start()


    # Parse arguments
    args = parser.parse_args()
    logger.info("ℹ️  Selected UI: %s", args.ui)
    if args.ui=="webUI":
        ui = WebUI(mqtt_app)
    elif args.ui=="console":
        ui = ConsoleUI(mqtt_app)

    if ui is not None:
        ui.run_ui()


if __name__ == "__main__":
    main()
