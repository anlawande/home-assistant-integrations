from .ring_device import RingContactSensor


class RingApi:
    @classmethod
    async def get_all_data(cls):
        ring_device = RingContactSensor()
        ring_device.state.update({
            "contact": True,
            "bypass": True,
        })
        return {
            "sensors": {
                ring_device.device_id: ring_device
            },
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
