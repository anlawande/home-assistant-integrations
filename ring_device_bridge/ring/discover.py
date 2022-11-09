from .ring_api import RingApi


class Discover:

    @staticmethod
    async def discover():
        return await RingApi.get_all_devices()

    @staticmethod
    async def discover_single(device_id: str):
        return await RingApi.get_by_device_id(device_id)
