from dataclasses import dataclass


@dataclass
class PcUtilsSettings:
    enableShutdown: bool = True
    enableReboot: bool = True
    
