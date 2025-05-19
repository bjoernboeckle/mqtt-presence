from dataclasses import dataclass

@dataclass
class MqttSensorStateData:
    cpu_freq: str = None
    memory_usage: str = None
    cpu_load: str = None
    disk_usage_root: str = None
    disk_free_root: str = None
    net_bytes_sent: str = None
    net_bytes_recv: str = None
    cpu_temp: str = None

    def __getitem__(self, key):
        return getattr(self, key)
    
    def __setitem__(self, key, value):
        setattr(self, key, value)

@dataclass
class MqttBinarySensorData:
    status: str = None

    def __getitem__(self, key):
        return getattr(self, key)
    
    def __setitem__(self, key, value):
        setattr(self, key, value)
