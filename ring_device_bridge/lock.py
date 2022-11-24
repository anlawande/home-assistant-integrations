"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.lock import LockEntity
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.core import callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import RingDeviceDataUpdateCoordinator
from .entity import CoordinatedRingDeviceEntity
from .ring import RingDevice, RingDeviceType


async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switches."""
    device_id: str = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = RingDeviceDataUpdateCoordinator.get_instance()
    await coordinator.async_config_entry_first_refresh()

    device = coordinator.get_device_data(device_id)
    if device is None or device.device_type != RingDeviceType.RING_SMART_LOCK:
        return

    entities: list = [LockSensorEntity(device, coordinator, "locked")]

    async_add_entities(entities)


class LockSensorEntity(CoordinatedRingDeviceEntity, LockEntity):
    """Representation of a Sensor."""

    _attr_device_class = SensorDeviceClass.BATTERY

    def __init__(self, device: RingDevice, coordinator: RingDeviceDataUpdateCoordinator, state_identifier: str):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(device, coordinator)
        self._attr_unique_id = f"{device.device_id}_lock"
        self._attr_name = f"{device.alias} Lock"
        self.state_identifier = state_identifier

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        device = self.coordinator.get_device_data(self.device.device_id)
        if device is None:
            return
        self._attr_is_locked = device.state[self.state_identifier]
        self.async_write_ha_state()
