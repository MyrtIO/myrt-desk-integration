"""MyrtDesk height intergration"""
from datetime import timedelta
import logging
from homeassistant import config_entries, core
from homeassistant.const import DATA_BYTES
from homeassistant.components.number import NumberEntity
from myrt_desk_api.system import MyrtDeskSystem

from .const import DOMAIN, DEVICE_INFO

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=5)

async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Set up desk sensors."""
    desk = hass.data[DOMAIN][config_entry.entry_id]["desk"]
    async_add_entities([MyrtDeskHeap(desk.system)], update_before_add=True)

class MyrtDeskHeap(NumberEntity):
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

    def __init__(self, system: MyrtDeskSystem):
        super().__init__()
        self._system = system

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def native_value(self):
        """Return the entity value to represent the entity state."""
        return self._value

    async def async_update(self) -> None:
        """Update the current value."""
        try:
            self._value = await self._system.read_heap()
            self._available = True
        except IOError:
            self._available = False

