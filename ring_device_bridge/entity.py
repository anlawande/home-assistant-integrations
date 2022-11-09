"""Common code for ring_device_bridge."""
from __future__ import annotations

from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .ring import RingDevice
from .const import DOMAIN
from .coordinator import RingDeviceDataUpdateCoordinator


class CoordinatedRingDeviceEntity(CoordinatorEntity[RingDeviceDataUpdateCoordinator]):
    """Common base class for all coordinated ring_device_bridge entities."""

    state_identifier: str

    def __init__(
        self, device: RingDevice, coordinator: RingDeviceDataUpdateCoordinator
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.device: RingDevice = device

    @property
    def device_info(self) -> DeviceInfo:
        """Return information about the device."""
        return DeviceInfo(
            connections={(dr.CONNECTION_NETWORK_MAC, self.device.mac)},
            identifiers={(DOMAIN, str(self.device.device_id))},
            manufacturer="Ring",
            model=self.device.model,
            name=self.device.alias,
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = self.coordinator.data["sensors"][self.device.device_id].state[self.state_identifier]
        self.async_write_ha_state()
