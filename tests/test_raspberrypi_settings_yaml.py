import os
import yaml
import pytest
from mqtt_presence.devices.raspberrypi.raspberrypi_settings_yaml import RaspberryPiSettingsYaml
from mqtt_presence.devices.raspberrypi.raspberrypi_data import RaspberryPiSettings, GpioMode, Gpio

@pytest.fixture
def sample_settings(tmp_path):
    settings = RaspberryPiSettings(
        enable_raspberrypi=True,
        simulated=False,
        gpios=[
            Gpio(mode=GpioMode.LED, number=19, friendly_name="Red"),
            Gpio(mode=GpioMode.LED, number=21, friendly_name="Blue"),
        ]
    )
    file_path = tmp_path / "test_raspi.yaml"
    RaspberryPiSettingsYaml.save_raspberry_settings(settings, file_path)
    return file_path

def test_yaml_contains_top_level_fields(sample_settings):
    with open(sample_settings, "r") as f:
        data = yaml.safe_load(f)

    assert "enable_raspberrypi" in data
    assert data["enable_raspberrypi"] is True

    assert "simulated" in data
    assert data["simulated"] is False

    assert "gpios" in data
    assert len(data["gpios"]) == 2
    assert data["gpios"][0]["friendly_name"] == "Red"
