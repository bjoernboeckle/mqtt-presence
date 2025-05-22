import yaml
import pytest
from mqtt_presence import RaspberryPiSettingsYaml, GpioButton_Function

@pytest.fixture
def minimal_button_yaml(tmp_path):
    # YAML mit nur einer Funktion gesetzt
    data = {
        "enable_raspberrypi": True,
        "simulated": False,
        "gpios": [
            {
                "mode": "BUTTON",
                "number": 16,
                "friendly_name": "Powerdown",
                "button": {
                    "bounce_s": 0.1,
                    "pull_up": True,
                    "function_held": "SHUTDOWN"
                    # function_pressed und function_released fehlen absichtlich
                }
            }
        ]
    }
    file_path = tmp_path / "partial_button.yaml"
    with open(file_path, "w") as f:
        yaml.dump(data, f)
    return file_path

def test_load_partial_button_function(minimal_button_yaml):
    settings = RaspberryPiSettingsYaml.load_raspberry_settings(minimal_button_yaml)

    assert settings.enable_raspberrypi is True
    assert settings.simulated is False
    assert len(settings.gpios) == 1

    button_gpio = settings.gpios[0]
    assert button_gpio.friendly_name == "Powerdown"
    assert button_gpio.button is not None
    assert button_gpio.button.function_held == GpioButton_Function.SHUTDOWN
    assert button_gpio.button.function_pressed is None
    assert button_gpio.button.function_released is None
