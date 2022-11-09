from enum import Enum
from typing import Dict


class RingDeviceType(Enum):
    RING_CONTACT_SENSOR=1
    RING_SMART_LOCK=1


class RingDevice:
    device_type: RingDeviceType

    def __init__(self):
        self.host: str = "192.0.0.1"
        self.mac: str = "aaaa:bbbb:cccc:dddd::e"
        self.device_id: str = "aaaa:bbbb:cccc:dddd::e"
        self.model: str = "Ring Contact Sensor (2nd Gen)"
        self.alias: str = "Front door"
        self.state: Dict = {}


class RingContactSensor(RingDevice):
    def __init__(self):
        super(RingContactSensor, self).__init__()
        self.device_type = RingDeviceType.RING_CONTACT_SENSOR


class RingDeviceException(Exception):
    pass
