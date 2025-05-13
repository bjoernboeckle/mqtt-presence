import re, os, sys, platform, socket, signal

import logging
logger = logging.getLogger(__name__)



class Tools:
    def is_debugger_active():
        return sys.gettrace() is not None or os.getenv("DEBUG") == "1"

    @staticmethod
    def is_NoneOrEmpty(value) -> bool:
        return value is None or (isinstance(value, str) and value.strip() == "")    


    @staticmethod
    def sanitize_mqtt_topic(topic: str) -> str:
        # Remove all chars except: a-zA-Z0-9/_-
        sanitized = re.sub(r'[^a-zA-Z0-9/_-]', '', topic)
        return sanitized.lower()

    @staticmethod
    def getPCName() -> str:
        return socket.gethostname()


    @staticmethod
    def exitApplication():
        #os.kill(os.getpid(), signal.SIGINT)
        #os._exit(0)
        sys.exit()


    @staticmethod
    def shutdown():
        system = platform.system()
        if system == "Windows": os.system("shutdown /s /t 0")
        elif system in ["Linux", "Darwin"]: os.system("sudo shutdown -h now")


    @staticmethod
    def reboot():
        system = platform.system()
        if system == "Windows": os.system("shutdown /r /t 0")
        elif system in ["Linux", "Darwin"]: os.system("sudo shutdown -r now")


    @staticmethod
    def logPlatform():
        system = platform.system()
        machine = platform.machine()
        
        if system == "Windows":
            logger.info("🪟 Running on Windows")
        elif system == "Linux":
            if "arm" in machine or "aarch64" in machine:
                logger.info("🍓 Running on Raspberry Pi (likely)")
            else:
                logger.info("🐧 Running on generic Linux")
        elif system == "Darwin":
            logger.info("🍏 Running on macOS")
        else:
            logger.warning(f"Unknown system: {system}")
            sys.exit(1)


    @staticmethod
    def resource_path(relative_path):
        try:
            # Bei PyInstaller ist _MEIPASS der temporäre Ordner
            base_path = sys._MEIPASS  
        except AttributeError:
            base_path = os.path.abspath(os.path.dirname(__file__))  # Normaler Modus
        
        return os.path.join(base_path, relative_path)