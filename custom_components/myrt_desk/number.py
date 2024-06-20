"""MyrtDesk height intergration"""
from homeassistant import config_entries, core
from homeassistant.const import UnitOfLength
from homeassistant.components.number import NumberEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import callback

from .coordinator import MyrtDeskCoordinator
from .const import DOMAIN, DEVICE_INFO
from .api import DeskAPI

async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Set up desk light."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([MyrtDeskHeight(
        data["coordinator"],
        data["api"]
    )])

class MyrtDeskHeight(CoordinatorEntity, NumberEntity):
    """MyrtDesk legs entity"""
    _attr_name = "MyrtDesk Height"
    _available = False
    _value = 65
    _api: DeskAPI = None
    _attr_device_info = DEVICE_INFO

    def __init__(self, coordinator: MyrtDeskCoordinator, api: DeskAPI):
        super().__init__(coordinator)
        self._api = api

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement of desk height"""
        return UnitOfLength.CENTIMETERS

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the height."""
        return "myrt_desk_height"

    @property
    def icon(self):
        return "mdi:counter"

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def native_value(self):
        """Return the entity value to represent the entity state."""
        return self._value

    @property
    def native_min_value(self):
        """Return the minimum value."""
        return 65

    @property
    def native_max_value(self):
        """Return the maximum value."""
        return 125

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        value = self.coordinator.data["height"]
        self._value = value / 10
        self._available = True
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        try:
            await self._api.set_height(int(value * 10))
            self._value = value
            self._available = True
        except:  # noqa: E722
            self._available = False
        self.async_write_ha_state()
