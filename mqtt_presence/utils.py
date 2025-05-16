import os
import platform
import re
import socket
import sys
import logging

from pathlib import Path
from platformdirs import user_cache_dir, user_config_dir, user_log_dir

logger = logging.getLogger(__name__)

class Tools:
    APP_NAME = "mqtt-presence"

    @staticmethod
    def is_debugger_active():
        try:
            return sys.gettrace() is not None or os.getenv("DEBUG") == "1"
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.warning("Fehler beim Prüfen des Debuggers: %s", e)
        return False


    @staticmethod
    def is_none_or_empty(value) -> bool:
        return value is None or (isinstance(value, str) and value.strip() == "")


    @staticmethod
    def sanitize_mqtt_topic(topic: str) -> str:
        # Remove all chars except: a-zA-Z0-9/_-
        sanitized = re.sub(r'[^a-zA-Z0-9/_-]', '', topic)
        return sanitized.lower()

    @staticmethod
    def get_pc_name() -> str:
        return socket.gethostname()


    @staticmethod
    def exit_application():
        #os.kill(os.getpid(), signal.SIGINT)
        #os._exit(0)
        sys.exit()


    @staticmethod
    def shutdown():
        system = platform.system()
        if system == "Windows":
            os.system("shutdown /s /t 0")
        elif system in ["Linux", "Darwin"]:
            os.system("sudo shutdown -h now")


    @staticmethod
    def reboot():
        system = platform.system()
        if system == "Windows":
            os.system("shutdown /r /t 0")
        elif system in ["Linux", "Darwin"]:
            os.system("sudo shutdown -r now")




    @staticmethod
    def resource_path(relative_path):
        try:
            # PyInstaller i _MEIPASS  temp Dir
            base_path = sys._MEIPASS    # pylint: disable=protected-access
        except AttributeError:
            base_path = os.path.abspath(os.path.dirname(__file__))  # Normale Mode

        return os.path.join(base_path, relative_path)


    @staticmethod
    def get_config_path(app_name: str, filename: str = "config.yaml") -> Path:
        """
        Returns the path to the configuration file and creates the directory if needed.
        """
        config_dir = Path(user_config_dir(app_name))
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / filename

    @staticmethod
    def get_log_path(app_name: str, filename: str = "app.log") -> Path:
        """
        Returns the path to the log file and creates the directory if needed.
        """
        log_dir = Path(user_log_dir(app_name))
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir / filename

    @staticmethod
    def get_cache_path(app_name: str, filename: str = "") -> Path:
        """
        Returns the path to the cache directory or a cache file and creates the directory if needed.
        If filename is empty, only the directory path is returned.
        """
        cache_dir = Path(user_cache_dir(app_name))
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir / filename if filename else cache_dir
