"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
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
    if device is None:
        return
    if device.device_type != RingDeviceType.RING_CONTACT_SENSOR:
        return

    entities: list = [ContactSensorEntity(device, coordinator, "contact"),
                      ContactBypassSensorEntity(device, coordinator, "bypassed")]

    async_add_entities(entities)


class ContactSensorEntity(CoordinatedRingDeviceEntity, BinarySensorEntity):
    """Representation of a Sensor."""

    _attr_device_class = BinarySensorDeviceClass.WINDOW

    def __init__(self, device: RingDevice, coordinator: RingDeviceDataUpdateCoordinator, state_identifier: str):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(device, coordinator)
        self._attr_unique_id = f"{device.device_id}_contact"
        self._attr_name = f"{device.alias} Contact Sensor"
        self.state_identifier = state_identifier


class ContactBypassSensorEntity(CoordinatedRingDeviceEntity, BinarySensorEntity):
    """Representation of a Sensor."""

    _attr_device_class = BinarySensorDeviceClass.SAFETY

    def __init__(self, device: RingDevice, coordinator: RingDeviceDataUpdateCoordinator, state_identifier: str):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(device, coordinator)
        self._attr_unique_id = f"{device.device_id}_contact_bypass"
        self._attr_name = f"{device.alias} Contact Sensor Bypass"
        self.state_identifier = state_identifier
