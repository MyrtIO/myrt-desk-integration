"""MyrtDesk height intergration"""
from homeassistant import config_entries, core
from homeassistant.const import LENGTH_CENTIMETERS
from homeassistant.components.number import NumberEntity
from myrt_desk_api.legs import MyrtDeskLegs

from .const import DOMAIN, DEVICE_INFO

async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Set up desk light."""
    desk = hass.data[DOMAIN][config_entry.entry_id]["desk"]
    async_add_entities([MyrtDeskHeight(desk.legs)], update_before_add=True)

class MyrtDeskHeight(NumberEntity):
    """MyrtDesk legs entity"""
    _attr_name = "MyrtDesk Height"
    _available = False
    _value = 65
    _legs: MyrtDeskLegs = None
    _attr_device_info = DEVICE_INFO

    def __init__(self, legs: MyrtDeskLegs):
        super().__init__()
        self._legs = legs

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement of desk height"""
        return LENGTH_CENTIMETERS

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

    async def async_update(self) -> None:
        """Update the current value."""
        value = await self._legs.get_height()
        self._value = value / 10
        self._available = True

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        await self._legs.set_height(int(value * 10))
        self._value = value
        self._available = True
