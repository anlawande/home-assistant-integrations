"""Platform for sensor integration."""
from datetime import timedelta
import logging

import async_timeout

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

DOMAIN = "ring_device_bridge"

_LOGGER = logging.getLogger(__name__)


class MyAPI:

    async def fetch_data(self, session):
        async with session.get('http://localhost:3123/entities') as resp:
            return await resp.json()


class MyCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="My sensor",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=5),
        )
        self.my_api = MyAPI()
        self.session = async_get_clientsession(self.hass)

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(10):
                return await self.my_api.fetch_data(self.session)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

