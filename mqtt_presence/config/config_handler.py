import os
import logging
from dataclasses import fields, is_dataclass, MISSING, asdict
from typing import Type, TypeVar, Optional, List, Any, Dict
from pathlib import Path
from enum import Enum
from functools import partial
from copy import deepcopy
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.representer import RoundTripRepresenter
from ruamel.yaml.constructor import RoundTripConstructor
from dacite import from_dict, Config as DaciteConfig
from cryptography.fernet import Fernet

from mqtt_presence.config.configuration import Configuration
from mqtt_presence.utils import Tools
from mqtt_presence.version import NAME
from mqtt_presence.devices.raspberrypi.raspberrypi_data import RaspberryPiSettings
from mqtt_presence.devices.raspberrypi.raspberrypi_data import GpioMode, GpioButton_Function
from mqtt_presence.devices.pc_utils.pc_utils_data import PcUtilsSettings
from mqtt_presence.devices.device_data import HomeassistantType

logger = logging.getLogger(__name__)


SECRET_KEY_FILE = "secret.key"
CONFIG_DATA_FILE = "configuration.yaml"
PASSWORD_FILE = "password.key"


class ConfigYamlHelper:

    # Convert strings back to Enums
    @staticmethod
    def deserialize_enum(value: Any, enum_classes: list = [GpioMode, GpioButton_Function, HomeassistantType]) -> Any:
        """Recursively converts string values to their corresponding Enums."""
        if isinstance(value, str):
            for enum_class in enum_classes:
                try:
                    return enum_class(value)
                except ValueError:
                    continue
        if isinstance(value, dict):
            return {k: ConfigYamlHelper.deserialize_enum(v, enum_classes) for k, v in value.items()}
        if isinstance(value, list):
            return [ConfigYamlHelper.deserialize_enum(v, enum_classes) for v in value]
        return value


    # Convert Enum values to strings before saving
    @staticmethod
    def dataclass_to_serializable(obj):
        if is_dataclass(obj):
            result = {}
            for key, value in asdict(obj).items():
                if value is None or isinstance(value, partial):
                    continue  # ⛔ None-Werte auslassen
                result[key] = ConfigYamlHelper.dataclass_to_serializable(value)
            return result

        elif isinstance(obj, Enum):
            return obj.value

        elif isinstance(obj, list):
            return [ConfigYamlHelper.dataclass_to_serializable(v) for v in obj]

        elif isinstance(obj, dict):
            return {
                k: ConfigYamlHelper.dataclass_to_serializable(v)
                for k, v in obj.items()
                if v is not None  # ⛔ None-Werte in Dicts auslassen
            }
        elif isinstance(obj, partial):
            return ""
        else:
            return obj


    @staticmethod
    def remove_defaults(current_obj: Configuration, default_obj: Configuration) -> dict:
        """
        Entfernt aus current_obj alle Werte, die mit default_obj identisch sind,
        und gibt ein dict mit nur abweichenden Werten zurück.
        """
        def prune(current, default):
            if isinstance(current, dict) and isinstance(default, dict):
                pruned = {}
                for k in current:
                    if k not in default:
                        pruned[k] = current[k]
                    else:
                        child = prune(current[k], default[k])
                        if child not in ({}, [], None):
                            pruned[k] = child
                return pruned
            else:
                return current if current != default else None

        current_dict = ConfigYamlHelper._to_dict(current_obj)
        default_dict = ConfigYamlHelper._to_dict(default_obj)
        pruned = prune(current_dict, default_dict)
        return pruned or {}


    @staticmethod
    def _to_dict(obj):
        if is_dataclass(obj):
            return {field.name: ConfigYamlHelper._to_dict(getattr(obj, field.name)) for field in fields(obj)}
        if isinstance(obj, list):
            return [ConfigYamlHelper._to_dict(value) for value in obj]
        if isinstance(obj, dict):
            return {k: ConfigYamlHelper._to_dict(value) for k, value in obj.items()}

        return obj


class ConfigHandler:
    def __init__(self, data_path: str = None):
        self.data_path = Path(data_path or Tools.get_data_path(NAME))
        self._secret_file = str(self.data_path / SECRET_KEY_FILE)
        self._config_file = str(self.data_path / CONFIG_DATA_FILE)
        self._passowrd_file = str(self.data_path / PASSWORD_FILE)
        self._yaml = self._create_yaml()
        self._initialize_data_path()
        self._fernet = Fernet(self._load_key())


    def _create_yaml(self):
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.default_flow_style = False
        return yaml

    def _initialize_data_path(self):
        if not self.data_path.exists():
            try:
                self.data_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error("❌ Could not create data path: %s", e)
                raise
        else:
            logger.debug("ℹ️  Data path already exists: %s", self.data_path)


    def _initialize_config_file(self):
        if not os.path.exists(self._config_file):
            logger.warning("⚠️ No configuration file found in: %s. Create default.", self._config_file)
            try:
                # Create an empty configuration file
                self.save_config(self.get_default_config(), None, add_default_comment=True)
                logger.info("📝 Created default configuration file: %s", self._config_file)
            except Exception as e:
                logger.error("❌ Could not create configuration file: %s", e)
                raise
        else:
            logger.debug("ℹ️  Configuration file already exists: %s", self._config_file)


    def get_default_config(self) -> Configuration:
        """
        Returns the default configuration as a Configuration dataclass instance.
        This is useful for creating a new configuration file or resetting the current one.
        :return: Default Configuration dataclass instance.
        """
        config = Configuration()
        config.mqtt.broker.client_id = Tools.sanitize_mqtt_topic(f"{NAME}_{Tools.get_pc_name()}")
        config.mqtt.broker.prefix = Tools.sanitize_mqtt_topic(f"{NAME}/{Tools.get_pc_name()}")
        config.mqtt.homeassistant.device_name = Tools.get_pc_name()

        # Set default values for the devices
        config.devices.pc_utils = PcUtilsSettings()
        if Tools.is_rasppery_pi():
            config.devices.raspberryPi = RaspberryPiSettings.get_default_raspberrypi_settings()
        else:
            config.devices.raspberryPi.enabled = False


        # Set default values for conatiner environment
        if Tools.is_in_container():
            config.devices.pc_utils.enableReboot = False
            config.devices.pc_utils.enableShutdown = False

        return config


    def _load_key(self):
        if not os.path.exists(self._secret_file):
            return self._generate_key()
        with open(self._secret_file, "rb") as file_secret:
            return file_secret.read()

    def _generate_key(self):
        dir_path = os.path.dirname(self._secret_file)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        key = Fernet.generate_key()
        with open(self._secret_file, "wb") as file_secret:
            file_secret.write(key)
        return key




    def load_config(self) -> Configuration:
        """
        Load a yaml configuration file and convert it to a Configuration dataclass.
        If the file does not exist, a FileNotFoundError is raised.
        If the file is not a valid YAML, a yaml.YAMLError is raised.
        If the YAML contains unknown fields, they are ignored.
        :param path: Path to the YAML configuration file.
        :return: Configuration dataclass instance.
        :raises FileNotFoundError: If the file does not exist.
        :raises yaml.YAMLError: If the file is not a valid YAML.
        :raises ValueError: If a required field is missing and has no default value.
        :raises TypeError: If the YAML data cannot be converted to the Configuration dataclass.
        """
        config_path = Path(self._config_file)
        if not config_path.exists():
            self._initialize_config_file()

        with config_path.open("r", encoding="utf-8") as f:
            yaml_data = self._yaml.load(f)
        if yaml_data is None:
            logger.warning("⚠️ Configuration file is empty or not valid YAML. Using default configuration.")
            return self.get_default_config()  # Return default configuration if file is empty

        # Convert Enums in nested fields
        parsed_yaml = ConfigYamlHelper.deserialize_enum(yaml_data.get("app", {}))

        # Convert YAML data to Configuration dataclass
        config = from_dict(
            data_class=Configuration,
            data=parsed_yaml,
            config=DaciteConfig(strict=False)
        )


        return config


    def save_config(self, config: Configuration, password: str, add_default_comment: bool = False):
        try:
            config_path = Path(self._config_file)

            original_yaml = None
            if config_path.exists():
                with config_path.open("r", encoding="utf-8") as f:
                    original_yaml = self._yaml.load(f)

            self._save_config(self._config_file, config, password, original_yaml=original_yaml, add_default_comment=add_default_comment)
        except Exception as e:
            logger.exception("❌ Failed to save config")




    def _save_config(self, path: str, config: Configuration, password: str, original_yaml: Optional[dict] = None, add_default_comment: bool = False):
        """
        Save a Configuration dataclass to a YAML file.
        If original_yaml is provided, it will be used to preserve comments and formatting.
        :param path: Path to the YAML configuration file.
        :param config: Configuration dataclass instance to save.
        :param original_yaml: Original YAML data to preserve comments and formatting.
        :raises FileNotFoundError: If the directory does not exist.
        :raises yaml.YAMLError: If the data cannot be converted to YAML.
        :raises ValueError: If a required field is missing and has no default value.
        :raises TypeError: If the config is not a valid Configuration dataclass.
        :return: None
        :raises Exception: If the file cannot be written.
        """
        self.save_password(password)

        # TODO: issues after a value was changed it will not be updated any more if set to default value!
        # Default config for comparison (use unchanged defaults, to store pc dependent defaults)
        #default_config = Configuration()

        # Keep only the fields that differ from the default configuration
        reduced_config_dict = config # ConfigYamlHelper.remove_defaults(config, default_config)

        # Convert Enums to strings
        reduced_config_dict = ConfigYamlHelper.dataclass_to_serializable(reduced_config_dict)

        if original_yaml:
            def merge(d_old, d_new):
                for k, v in d_new.items():
                    if k in d_old and isinstance(d_old[k], dict) and isinstance(v, dict):
                        merge(d_old[k], v)
                    else:
                        d_old[k] = v
            merged_yaml = deepcopy(original_yaml)
            merge(merged_yaml, {"app": reduced_config_dict})
        else:
            merged_yaml = CommentedMap({"app": reduced_config_dict})

        with open(self._config_file, "w", encoding="utf-8") as f:
            if add_default_comment and hasattr(merged_yaml, "yaml_set_start_comment"):
                merged_yaml.yaml_set_start_comment(
                    "Configuration file for MQTT Presence\n"
                    "Please refer to the documentation for details on how to configure."
                )
            self._yaml.dump(merged_yaml, f)




    def save_password(self, password: str):
        """
        Save the encrypted password to the password file.
        If the password is empty, the file is cleared.
        If the password is None the file is not changed.
        :param password: Password to save as a string.
        """
        if (password is None):
            return  # Do not change the file if password is None
        encrypted_password = self.get_encrypt_password(password)
        with open(self._passowrd_file, "w", encoding="utf-8") as f:
            f.write(encrypted_password)



    def get_password(self) -> str:
        """
        Load the encrypted password from the password file.
        If the file does not exist, an empty string is returned.
        :return: Encrypted password as a string.
        """
        if not os.path.exists(self._passowrd_file):
            return ""
        with open(self._passowrd_file, "r", encoding="utf-8") as f:
            return self.get_decrypt_password(f.read().strip())


    def get_encrypt_password(self, plain_password):
        return "" if Tools.is_none_or_empty(plain_password) else self._encrypt(plain_password)

    def get_decrypt_password(self, encrypted_password):
        return "" if Tools.is_none_or_empty(encrypted_password) else self._decrypt(encrypted_password)

    def _encrypt(self, value):
        return self._fernet.encrypt(value.encode()).decode()

    def _decrypt(self, value):
        return self._fernet.decrypt(value.encode()).decode()

