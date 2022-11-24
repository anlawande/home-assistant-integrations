"""Component to embed TP-Link smart home devices."""
from __future__ import annotations

import json
from datetime import timedelta, datetime
import logging
from typing import Dict, Optional

import async_timeout
from homeassistant.core import HomeAssistant
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .ring import RingApi, RingDevice, RingDeviceException

_LOGGER = logging.getLogger(__name__)

REQUEST_REFRESH_DELAY = 0.35


class RingDeviceDataUpdateCoordinator(DataUpdateCoordinator):
    """DataUpdateCoordinator to gather data for a specific RingDevice device."""
    instance: Optional[RingDeviceDataUpdateCoordinator] = None

    @classmethod
    def create(cls, hass: HomeAssistant):
        cls.instance = RingDeviceDataUpdateCoordinator(hass)

    @classmethod
    def get_instance(cls) -> RingDeviceDataUpdateCoordinator:
        assert cls.instance is not None
        return cls.instance

    def __init__(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Initialize DataUpdateCoordinator to gather data for specific SmartPlug."""
        update_interval = timedelta(seconds=5)
        super().__init__(
            hass,
            _LOGGER,
            name="RingDeviceDataUpdateCoordinator",
            update_interval=update_interval,
            # We don't want an immediate refresh since the device
            # takes a moment to reflect the state change
            request_refresh_debouncer=Debouncer(
                hass, _LOGGER, cooldown=REQUEST_REFRESH_DELAY, immediate=False
            ),
        )

    async def _async_update_data(self) -> Dict:
        """Fetch all device and sensor data from api."""
        try:
            async with async_timeout.timeout(10):
                return await RingApi.get_all_data()
        except Exception as ex:
            raise UpdateFailed(ex) from ex

    def get_device_data(self, device_id: str):
        for data_type in ["sensors", "locks"]:
            if device_id in self.data[data_type]:
                return self.data[data_type][device_id]

        return None
