import aiohttp
import logging
from datetime import datetime

from .ring_device import RingContactSensor, RingLock, RingAlarm

logger = logging.getLogger(__name__)

class MyAPI:
    session: aiohttp.ClientSession
    api_token: str
    last_fetch_ts: float
    data_cache: any
    fetch_in_progress: bool

    @classmethod
    def set_session(cls, session: aiohttp.ClientSession) -> None:
        cls.session = session
        cls.last_fetch_ts = datetime.now().timestamp()
        cls.data_cache = {}
        cls.fetch_in_progress = False

    @classmethod
    def set_api_token(cls, api_token: str):
        cls.api_token = api_token

    @classmethod
    async def fetch_data(cls):
        if cls.fetch_in_progress:
            return cls.data_cache
        now_ts = datetime.now().timestamp()
        if now_ts - cls.last_fetch_ts < 1.0 and cls.data_cache != {}:
            return cls.data_cache
        cls.fetch_in_progress = True
        try:
            async with cls.session.get(f"http://localhost:3123/entities?apiToken={cls.api_token}") as resp:
                data = await resp.json()
                cls.data_cache = data
                cls.last_fetch_ts = datetime.now().timestamp()
                cls.fetch_in_progress = False
                return data
        except Exception as e:
            logger.warning(e)
        finally:
            cls.fetch_in_progress = False
            return cls.data_cache

    @classmethod
    async def set_mode(cls, mode: str) -> None:
        async with cls.session.post(f"http://localhost:3123/alarm?apiToken={cls.api_token}", json={"mode": mode}) as resp:
            assert resp.status == 200


class RingApi:
    @classmethod
    def set_session(cls, session: aiohttp.ClientSession) -> None:
        MyAPI.set_session(session)

    @classmethod
    def set_api_token(cls, api_token: str) -> None:
        MyAPI.set_api_token(api_token)

    @classmethod
    async def get_all_data(cls):
        ring_data = await MyAPI.fetch_data()
        ring_data_sensors = ring_data.get("sensors", {})
        ring_data_locks = ring_data.get("locks", {})
        ring_data_alarms = ring_data.get("alarms", {})
        ring_sensors = {}
        for mac, device in ring_data_sensors.items():
            sensor = RingContactSensor(mac=mac, host=device["host"], device_id=mac,
                                       alias=device["name"], state=device["state"])
            ring_sensors[mac] = sensor

        ring_locks = {}
        for mac, device in ring_data_locks.items():
            lock = RingLock(mac=mac, host=device["host"], device_id=mac,
                            alias=device["name"], state=device["state"])
            ring_locks[mac] = lock

        ring_alarms = {}
        for mac, device in ring_data_alarms.items():
            alarm = RingAlarm(mac=mac, host=device["host"], device_id=mac,
                              alias="Ring Security Panel", state=device["alarmMode"])
            ring_alarms[mac] = alarm

        return {
            "sensors": ring_sensors,
            "locks": ring_locks,
            "alarms": ring_alarms,
        }

    @classmethod
    async def get_all_devices(cls):
        data = await cls.get_all_data()
        devices = {}
        for device_data in data.values():
            devices.update(device_data)

        return devices

    @classmethod
    async def get_by_device_id(cls, device_id: str):
        data = await cls.get_all_data()
        for device_data in data.values():
            try:
                return device_data[device_id]
            except:
                pass

        return None

    @classmethod
    async def set_mode(cls, mode: str):
        print("set_mode")
        await MyAPI.set_mode(mode)
