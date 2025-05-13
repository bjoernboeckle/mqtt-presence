from mqtt_presence.app_data import ConfigFiles, Configuration
from mqtt_presence.app_config import AppConfiguration
from mqtt_presence.utils import Tools

from dataclasses import fields, is_dataclass, MISSING
from typing import Type, TypeVar
from cryptography.fernet import Fernet
import yaml
import json
import os


import logging
logger = logging.getLogger(__name__)

DEFAULT_PASSWORD = "h7F$kP2!mA93X@vL"


class Config_Handler:
    def __init__(self, configFiles: ConfigFiles = None):
        self.configFiles = configFiles or ConfigFiles()
        self.fernet = Fernet(self._load_key())

    def _load_key(self):
        if not os.path.exists(self.configFiles.secretFile):
            return self._generate_key()
        with open(self.configFiles.secretFile, "rb") as f:
            return f.read()

    def _generate_key(self):
        dir_path = os.path.dirname(self.configFiles.secretFile)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)        
        key = Fernet.generate_key()
        with open(self.configFiles.secretFile, "wb") as f:
            f.write(key)
        return key



    # Load YAML file as AppConfiguration
    def load_config_yaml(self) -> AppConfiguration:
        if os.path.exists(self.configFiles.yamlFile):
            with open(self.configFiles.yamlFile, "r") as f:
                config = self._from_dict(AppConfiguration, yaml.safe_load(f))
            logger.info(f"✅ Configuration loaded from: {self.configFiles.yamlFile}")
            return config
        else:
            logger.info(f"⚠️ No configuration file found in: {self.configFiles.yamlFile}. Create default.")
            config = AppConfiguration()
            with open(self.configFiles.yamlFile, "w") as f_out:
                yaml.dump(self._to_dict(config), f_out)
            logger.info(f"📝 Default configuration written to: {self.configFiles.yamlFile}")
            return config


    def checkConfig(self, config: Configuration):
        if ( Tools.is_NoneOrEmpty(config.mqtt.homeassistant.device_name)): config.mqtt.homeassistant.device_name = Tools.getPCName()
        if ( Tools.is_NoneOrEmpty(config.mqtt.broker.prefix)): config.mqtt.broker.prefix = Tools.sanitize_mqtt_topic(config.mqtt.homeassistant.device_name)


    # Load config file as Configuration
    def load_config(self) -> Configuration:
        config = None
        try:
            with open(self.configFiles.configFile, "r") as f:
                raw_data = json.load(f)
                config = self._from_dict(Configuration, raw_data)
        except FileNotFoundError:
            logger.warning(f"⚠️ File '{self.configFiles.configFile}' not found – use defaults.")
            config = self._from_dict(Configuration, {})
            config.mqtt.broker.encrypted_password = self.get_encrypt_password(DEFAULT_PASSWORD)       
        
        # check cofig
        self.checkConfig(config)
        return config



    def save_config(self, config: Configuration):
        def to_diff_dict(obj, default_obj):
            if is_dataclass(obj):
                result = {}
                for f in fields(obj):
                    value = getattr(obj, f.name)
                    default_value = getattr(default_obj, f.name)

                    # check recursiv for nested data
                    diff = to_diff_dict(value, default_value)
                    if diff != {}:
                        result[f.name] = diff
                return result
            elif isinstance(obj, list):
                return obj if obj != default_obj else {}
            elif isinstance(obj, dict):
                return obj if obj != default_obj else {}
            else:
                return obj if obj != default_obj else {}

        # create default instance to compare
        default_config = Configuration()

        #create a dictionary, with differences
        diff_dict = to_diff_dict(config, default_config)

        with open(self.configFiles.configFile, "w") as f:
            json.dump(diff_dict, f, indent=2)


    def get_encrypt_password(self, plain_passowrd):
        return self._encrypt(plain_passowrd)

    def get_decrypt_password(self, encryptedPassword):
        return DEFAULT_PASSWORD if (encryptedPassword is None) else self._decrypt(encryptedPassword)

    def _encrypt(self, value):
        return self.fernet.encrypt(value.encode()).decode()

    def _decrypt(self, value):
        return self.fernet.decrypt(value.encode()).decode()
    

    # Typehelper for generic load
    T = TypeVar("T")
    def _from_dict(self, data_class: Type[T], data: dict) -> T:
        """
        Recursive conversion of a dictionary into a dataclass instance,
        with support for default values and nested classes.
        """
        kwargs = {}
        for f in fields(data_class):
            value = data.get(f.name, MISSING)
            if value is MISSING:
                # Field not found in yaml
                if f.default is not MISSING:
                    kwargs[f.name] = f.default
                elif f.default_factory is not MISSING:  # type: ignore
                    kwargs[f.name] = f.default_factory()  # type: ignore
                else:
                    raise ValueError(f"Feld '{f.name}' fehlt in Daten und hat keinen Defaultwert.")
            else:
                # Value not set → check if nested dataclass
                if is_dataclass(f.type) and isinstance(value, dict):
                    kwargs[f.name] = self._from_dict(f.type, value)
                else:
                    kwargs[f.name] = value

        return data_class(**kwargs)

    def _to_dict(self, obj):
        if is_dataclass(obj):
            return {f.name: self._to_dict(getattr(obj, f.name)) for f in fields(obj)}
        elif isinstance(obj, list):
            return [self._to_dict(v) for v in obj]
        elif isinstance(obj, dict):
            return {k: self._to_dict(v) for k, v in obj.items()}
        else:
            return obj
