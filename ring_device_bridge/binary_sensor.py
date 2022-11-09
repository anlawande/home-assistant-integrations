"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import RingDeviceDataUpdateCoordinator
from .entity import CoordinatedRingDeviceEntity
from .ring import RingDevice, RingContactSensor


async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switches."""
    device_id: str = hass.data[DOMAIN][config_entry.entry_id]
    device_bypass = RingContactSensor()
    device_contact = RingContactSensor()
    coordinator = RingDeviceDataUpdateCoordinator.get_instance()
    entities: list = [ContactSensorEntity(device_contact, coordinator, "contact"),
                      ContactBypassSensorEntity(device_bypass, coordinator, "bypass")]

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
