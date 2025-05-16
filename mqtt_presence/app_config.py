from dataclasses import dataclass, field

@dataclass
class MqttAppConfig:
    client_id: str = ""

@dataclass
class WebServerAppConfig:
    host: int = "0.0.0.0"
    port: int = 8000

@dataclass
class AppConfig:
    disableShutdown: bool = False    # pylint: disable=invalid-name
    webServer: WebServerAppConfig = field(default_factory=WebServerAppConfig)    # pylint: disable=invalid-name
    mqtt: MqttAppConfig = field(default_factory=MqttAppConfig)   # pylint: disable=invalid-name

@dataclass
class AppConfiguration:
    app: AppConfig = field(default_factory=AppConfig)
