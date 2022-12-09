"""Platform for sensor integration."""
from __future__ import annotations
from logging import getLogger

from homeassistant.core import callback
from homeassistant.components.alarm_control_panel import AlarmControlPanelEntity, AlarmControlPanelEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import RingDeviceDataUpdateCoordinator
from .entity import CoordinatedRingDeviceEntity
from .ring import RingApi, RingDevice, RingDeviceType

logger = getLogger(__name__)

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
    if device.device_type != RingDeviceType.RING_SECURITY_PANEL:
        return

    entities: list = [RingAlarmControlPanelEntity(device, coordinator)]

    async_add_entities(entities)


class RingAlarmControlPanelEntity(CoordinatedRingDeviceEntity, AlarmControlPanelEntity):
    """Representation of a Alarm Control Panel."""
    _attr_supported_features = AlarmControlPanelEntityFeature.ARM_AWAY | AlarmControlPanelEntityFeature.ARM_HOME

    def __init__(self, device: RingDevice, coordinator: RingDeviceDataUpdateCoordinator):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(device, coordinator)
        self._attr_unique_id = f"{device.device_id}_alarm"
        self._attr_name = device.alias

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        device = self.coordinator.get_device_data(self.device.device_id)
        if device is None:
            return
        self._attr_state = to_ha_alarm_state(device.state)
        self.async_write_ha_state()

    async def async_alarm_disarm(self, code=None) -> None:
        """Send disarm command."""
        await RingApi.set_mode("DISARMED")

    async def async_alarm_arm_home(self, code=None) -> None:
        """Send arm home command."""
        await RingApi.set_mode("HOME")

    async def async_alarm_arm_away(self, code=None) -> None:
        """Send arm away command."""
        await RingApi.set_mode("AWAY")


def to_ha_alarm_state(api_alarm_state):
    if api_alarm_state == "DISARMED":
        return "disarmed"
    if api_alarm_state == "HOME":
        return "armed_home"
    if api_alarm_state == "AWAY":
        return "armed_away"
