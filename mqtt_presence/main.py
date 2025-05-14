from mqtt_presence.mqtt_presence_app import MQTTPresenceApp#, MQTTPresenceAppSingleton
from mqtt_presence.utils import Tools
from mqtt_presence.web_ui import WebUI
from mqtt_presence.console_ui import ConsoleUI


import argparse
import signal, sys
import logging

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
    def stop(signum, frame):
        logger.info("🚪 Stop signal recived, exiting...")
        if (mqttAPP is not None): mqttAPP.exitApp()
        if (ui is not None): ui.stop()
        Tools.exitApplication()


    mqttAPP: MQTTPresenceApp = MQTTPresenceApp()
    ui = None

    startUpMsg = f"🚀 mqtt-presence startup (Version: {mqttAPP.version})"
    logger.info("\n\n")
    logger.info(startUpMsg)


    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    mqttAPP.start()


    # Parse arguments
    args = parser.parse_args()    
    logger.info(f"ℹ️  Selected UI: {args.ui}")        
    if (args.ui=="webUI"): ui = WebUI(mqttAPP)
    elif (args.ui=="console"): ui = ConsoleUI(mqttAPP)
    
    if (ui is not None): ui.runUI()


if __name__ == "__main__":
    main()
