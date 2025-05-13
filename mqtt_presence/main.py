from mqtt_presence.mqtt_presence_app import MQTTPresenceApp#, MQTTPresenceAppSingleton
from mqtt_presence.config_handler import Config_Handler
from mqtt_presence.app_data import ConfigFiles
from mqtt_presence.utils import Tools

import argparse
import signal, sys
import logging

# setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)  # Konsole
        #logging.FileHandler('log/mqtt_presence.log', mode='a', encoding='utf-8')  # Datei (append mode)
    ]
)
logger = logging.getLogger(__name__)




# define Arguemnts
parser = argparse.ArgumentParser(description="mqtt-presence")

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
        if (mqttAPP is not None):
            mqttAPP.exitApp()
        Tools.exitApplication()

    logger.info("🚀 mqtt-presence startup")
    # Parse arguments
    args = parser.parse_args()    
    logger.info(f"ℹ️  Selected UI: {args.ui}")

    mqttAPP: MQTTPresenceApp = MQTTPresenceApp()
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    mqttAPP.start()

    if (args.ui=="webUI"): mqttAPP.runWebUI()
    elif (args.ui=="console"): mqttAPP.runConsoleUI()


if __name__ == "__main__":
    main()
