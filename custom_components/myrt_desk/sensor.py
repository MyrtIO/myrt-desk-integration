"""MyrtDesk height intergration"""
import logging
from homeassistant import config_entries, core
from homeassistant.const import DATA_BYTES
from homeassistant.components.number import NumberEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import callback
from myrt_desk_api.system import MyrtDeskSystem

from .coordinator import MyrtDeskCoordinator
from .const import DOMAIN, DEVICE_INFO

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Set up desk sensors."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([MyrtDeskHeap(
        data["coordinator"],
        data["desk"].system
    )])

class MyrtDeskHeap(CoordinatorEntity, NumberEntity):
    """MyrtDesk free heap"""
    _attr_name = "MyrtDesk Free Heap"
    _attr_unique_id = "myrt_desk_free_heap"
    _attr_native_unit_of_measurement = DATA_BYTES
    _attr_native_max_value = 48904
    _attr_native_min_value = 0
    _attr_icon = "mdi:memory"
    _available = False
    _value = 0
    _system: MyrtDeskSystem = None
    _attr_device_info = DEVICE_INFO

    def __init__(self, coordinator: MyrtDeskCoordinator, system: MyrtDeskSystem):
        super().__init__(coordinator)
        self._system = system

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def native_value(self):
        """Return the entity value to represent the entity state."""
        return self._value

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._value = self.coordinator.data["heap"]
        self.async_write_ha_state()

