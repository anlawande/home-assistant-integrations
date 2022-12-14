"""Component to embed TP-Link smart home devices."""
from __future__ import annotations

from datetime import timedelta
from logging import getLogger
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_MAC,
    CONF_NAME,
    EVENT_HOMEASSISTANT_STARTED, CONF_API_TOKEN,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv, device_registry as dr, discovery_flow
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, PLATFORMS, CONF_API_HOST_AND_PORT
from .coordinator import RingDeviceDataUpdateCoordinator, RingDeviceException
from .ring import RingApi, RingDevice, Discover

DISCOVERY_INTERVAL = timedelta(minutes=15)

logger = getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_API_TOKEN): cv.string,
        vol.Required(CONF_API_HOST_AND_PORT): cv.string,
    }, extra=vol.ALLOW_EXTRA),
}, extra=vol.ALLOW_EXTRA)

@callback
def async_trigger_discovery(
    hass: HomeAssistant,
    discovered_devices: dict[str, RingDevice],
) -> None:
    """Trigger config flows for discovered devices."""
    for formatted_mac, device in discovered_devices.items():
        discovery_flow.async_create_flow(
            hass,
            DOMAIN,
            context={"source": config_entries.SOURCE_INTEGRATION_DISCOVERY},
            data={
                CONF_NAME: device.alias,
                CONF_HOST: device.host,
                CONF_MAC: formatted_mac,
            },
        )


async def async_discover_devices(hass: HomeAssistant) -> dict[str, RingDevice]:
    """Discover RingDevice devices on configured network interfaces."""
    all_devices = await Discover.discover()
    discovered_devices: dict[str, RingDevice] = {}
    for device in all_devices.values():
        discovered_devices[dr.format_mac(device.mac)] = device
    return discovered_devices


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the TP-Link component."""
    hass.data[DOMAIN] = {}
    RingDeviceDataUpdateCoordinator.create(hass)
    RingApi.configure_api(async_get_clientsession(hass), config[DOMAIN][CONF_API_HOST_AND_PORT], config[DOMAIN][CONF_API_TOKEN])

    if discovered_devices := await async_discover_devices(hass):
        async_trigger_discovery(hass, discovered_devices)

    async def _async_discovery(*_: Any) -> None:
        if discovered := await async_discover_devices(hass):
            async_trigger_discovery(hass, discovered)

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _async_discovery)
    async_track_time_interval(hass, _async_discovery, DISCOVERY_INTERVAL)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up RingDevice from a config entry."""
    try:
        device: RingDevice = await Discover.discover_single(entry.data[CONF_MAC])
    except RingDeviceException as ex:
        raise ConfigEntryNotReady from ex

    hass.data[DOMAIN][entry.entry_id] = device.device_id
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass_data: dict[str, Any] = hass.data[DOMAIN]
    device: RingDevice = hass_data[entry.entry_id].device
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass_data.pop(entry.entry_id)
    # await device.protocol.close()
    return unload_ok
