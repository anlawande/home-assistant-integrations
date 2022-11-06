"""Platform for sensor integration."""
from __future__ import annotations

from typing import Optional, Callable

from homeassistant.components.lock import LockEntity
from homeassistant.core import callback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType, HomeAssistantType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from . import MyCoordinator


async def async_setup_platform(
        hass: HomeAssistantType,
        config: ConfigType,
        async_add_entities: Callable,
        discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    coordinator = MyCoordinator(hass)

    await coordinator.async_config_entry_first_refresh()

    """Set up the sensor platform."""
    async_add_entities(
        Lock(coordinator, ent) for idx, ent in coordinator.data["locks"].items()
    )


class Lock(CoordinatorEntity, LockEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, ent):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self.idx = ent["id"]
        self._attr_unique_id = ent["id"]
        self._attr_name = ent["name"]

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_locked = self.coordinator.data["locks"][self.idx]["state"]
        self.async_write_ha_state()

