import logging
from typing import Optional
import serial
import time

from mqtt_presence.devices.device_data import DeviceData, DeviceType
from mqtt_presence.config.configuration import Configuration
from mqtt_presence.devices.mouse_jiggler.mouse_jiggler_data import MouseJigglerSettings, jigglerMode
from mqtt_presence.devices.device import Device
from mqtt_presence.devices.device_data import DeviceKey

logger = logging.getLogger(__name__)


class MouseJiggler(Device):
    def __init__(self, devcie_key: DeviceKey):
        super().__init__(devcie_key)


    def exit(self):
        super().exit()


    def init(self, config: Configuration, device_callback):
        super().init(config, device_callback)
        self.settings: MouseJigglerSettings = config.devices.mouse_jiggler
        if not self.settings.enabled:
            self._error_msg = "MouseJiggler device is disabled in the configuration. Apply to enable it."
            return

        self._status = True
        self.data.update( {
            # MQTT selects
            "jiggler_mode": DeviceData(friendly_name="Jiggler Mode", type = DeviceType.SELECT, icon = "mouse-pointer", data = self.settings.jigglerMode, options=["STOPPED", "ENABLED"]),
            # MQTT buttons
            #"test": DeviceData(friendly_name="Test button", type = DeviceType.BUTTON, icon="test-tube"),
            # MQTT sensors
            "serial_port": DeviceData(friendly_name="Serial port", type = DeviceType.SENSOR, icon = "serial-port", data = self.settings.serial_port),
            
        })
        #if self.settings.enableShutdown:
        #    self.data["shutdown"] = DeviceData(friendly_name="Shutdown PC", type = DeviceType.BUTTON, icon="power")

        
        self.setJigglerMode(jigglerMode.ENABLED if self.settings.jigglerMode else jigglerMode.STOPPED)
        


    def update_data(self, mqtt_online: Optional[bool] = False):
        if self.settings.enabled:
            self.data["jiggler_mode"].data = self.jiggler_mode == jigglerMode.ENABLED
            self.data["serial_port"].data = self.settings.serial_port
            pass


    def handle_command(self, data_key: str, function: str):
        logger.info("✏️  Device command: %s - %s", data_key, function)
        if data_key == "jiggler_mode":
            self.setJigglerMode(jigglerMode.ENABLED if function.upper() == "ENABLED" else jigglerMode.STOPPED)
            self.jiggler_mode = function
        elif ( data_key == "test"):
            logger.info("🧪 Test command")
        else:
            logger.warning("⚠️  Unknown Device command: %s - %s", data_key, function)



    def setJigglerMode(self, mode: jigglerMode):
        if mode == jigglerMode.ENABLED:
            self.jiggler_mode = jigglerMode.ENABLED
            logger.info("🟢  Mouse Jiggler enabled")
            # Here you would add the code to enable the mouse jiggler functionality
            self.sendSerialCommand("JIGGLERMODE=ENABLED\n")
        elif mode == jigglerMode.STOPPED:
            self.jiggler_mode = jigglerMode.STOPPED
            logger.info("🔴  Mouse Jiggler stopped")
            self.sendSerialCommand("JIGGLERMODE=STOPPED\n")
            # Here you would add the code to stop the mouse jiggler functionality
        else:
            logger.error("❌  Unknown jiggler mode: %s", mode)


    def sendSerialCommand(self, command: str):
        try:
            with serial.Serial(self.settings.serial_port, 115200, timeout=1, rtscts=False, dsrdtr=False) as ser:
                ser.setDTR(False)
                ser.setRTS(False)
                time.sleep(0.5)
                ser.write(command.encode())
                ser.close()
                logger.info(f"Sent command to {self.settings.serial_port} mouse jiggler: %s", command.encode())
        except serial.SerialException as e:
            logger.error("Failed to send command to mouse jiggler port %s: %s", self.settings.serial_port, e)