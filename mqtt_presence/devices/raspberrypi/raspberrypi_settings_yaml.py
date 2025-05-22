
import yaml
from enum import Enum
from dataclasses import is_dataclass, asdict

from mqtt_presence.devices.raspberrypi.raspberrypi_data import RaspberryPiSettings
from mqtt_presence.devices.raspberrypi.raspberrypi_data import RaspberryPiSettings, Gpio, GpioButton, GpioMode, GpioButton_Function


class IndentedDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


class RaspberryPiSettingsYaml:
    @staticmethod
    def enum_to_str(obj):
        if isinstance(obj, Enum):
            return obj.name
        return obj

    @staticmethod
    def dataclass_to_dict(obj):
        if is_dataclass(obj):
            result = {}
            for key, value in asdict(obj).items():
                if isinstance(value, Enum):
                    result[key] = value.name
                elif isinstance(value, list):
                    result[key] = [RaspberryPiSettingsYaml.dataclass_to_dict(v) for v in value]
                elif isinstance(value, dict):
                    result[key] = {k: RaspberryPiSettingsYaml.dataclass_to_dict(v) for k, v in value.items()}
                else:
                    result[key] = RaspberryPiSettingsYaml.enum_to_str(value)
            return result
        return obj
    
    @staticmethod
    def enum_to_str(obj):
        if isinstance(obj, Enum):
            return obj.name
        return obj
    
    def get_enum_safe(enum_class, value):
        if value is None:
            return None
        try:
            return enum_class[value]
        except (KeyError, TypeError):
            return None    

    @staticmethod
    def dataclass_to_serializable(obj):
        if is_dataclass(obj):
            result = {}
            for key, value in asdict(obj).items():
                if value is None:
                    continue  # ⛔ None-Werte auslassen
                result[key] = RaspberryPiSettingsYaml.dataclass_to_serializable(value)
            return result

        elif isinstance(obj, Enum):
            return obj.name

        elif isinstance(obj, list):
            return [RaspberryPiSettingsYaml.dataclass_to_serializable(v) for v in obj]

        elif isinstance(obj, dict):
            return {
                k: RaspberryPiSettingsYaml.dataclass_to_serializable(v)
                for k, v in obj.items()
                if v is not None  # ⛔ None-Werte in Dicts auslassen
            }

        else:
            return obj        
   


    @staticmethod
    def save_raspberry_settings(settings: RaspberryPiSettings, path: str):
        data = RaspberryPiSettingsYaml.dataclass_to_serializable(settings)
        with open(path, "w") as f:
            yaml.dump(data, f, Dumper=IndentedDumper, sort_keys=False, indent=2, default_flow_style=False)


    @staticmethod
    def load_raspberry_settings(path: str) -> RaspberryPiSettings:
        def parse_button(button_data):
            if not button_data:
                return None
            return GpioButton(
                bounce_s=button_data.get("bounce_s", 0.1),
                pull_up=button_data.get("pull_up", True),
                function_pressed=RaspberryPiSettingsYaml.get_enum_safe(GpioButton_Function, button_data.get("function_pressed")),
                function_released=RaspberryPiSettingsYaml.get_enum_safe(GpioButton_Function, button_data.get("function_released")),
                function_held=RaspberryPiSettingsYaml.get_enum_safe(GpioButton_Function, button_data.get("function_held")),
            )
        
        with open(path, "r") as f:
            raw = yaml.safe_load(f)

        settings = RaspberryPiSettings(
            enable_raspberrypi=raw.get("enable_raspberrypi", False),
            simulated=raw.get("simulated"),
            gpios=[]
        )

        for g in raw.get("gpios", []):
            mode = GpioMode[g.get("mode", "NONE")]
            button_data = g.get("button")

            if button_data:
                button = parse_button(button_data)
            else:
                button = None

            gpio = Gpio(
                mode=mode,
                number=g.get("number", -1),
                friendly_name=g.get("friendly_name", ""),
                button=button
            )
            settings.gpios.append(gpio)

        return settings
