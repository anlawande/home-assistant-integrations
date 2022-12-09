from enum import Enum
from typing import Dict


class RingDeviceType(Enum):
    RING_CONTACT_SENSOR = 1
    RING_SMART_LOCK = 2
    RING_SECURITY_PANEL = 3


class RingDevice:
    device_type: RingDeviceType

    def __init__(self, **kwargs):
        self.host: str = kwargs.get("host", "192.0.0.1")
        self.mac: str = kwargs.get("mac", "aaaa:bbbb:cccc:dddd::e")
        self.device_id: str = kwargs.get("device_id", "aaaa:bbbb:cccc:dddd::e")
        self.model: str = kwargs.get("model", "Ring Contact Sensor (2nd Gen)")
        self.alias: str = kwargs.get("alias", "Front door")
        self.state: Dict = kwargs.get("state", {})


class RingContactSensor(RingDevice):
    def __init__(self, **kwargs):
        super(RingContactSensor, self).__init__(**kwargs)
        self.model = "Ring Contact Sensor (2nd Gen)"
        self.device_type = RingDeviceType.RING_CONTACT_SENSOR


class RingLock(RingDevice):
    def __init__(self, **kwargs):
        super(RingLock, self).__init__(**kwargs)
        self.model = "Shlage Connect"
        self.device_type = RingDeviceType.RING_SMART_LOCK


class RingAlarm(RingDevice):
    def __init__(self, **kwargs):
        super(RingAlarm, self).__init__(**kwargs)
        self.model = "Ring Alarm Panel"
        self.device_type = RingDeviceType.RING_SECURITY_PANEL


class RingDeviceException(Exception):
    pass
