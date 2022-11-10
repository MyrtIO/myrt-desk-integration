"""MyrtDesk height intergration"""
from datetime import timedelta
import logging
from typing import Callable, Optional
from homeassistant.const import LENGTH_CENTIMETERS
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
from homeassistant.components.number import NumberEntity
from myrt_desk_api.legs import MyrtDeskLegs

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=3)

# pylint: disable-next=unused-argument
async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up desk height."""
    desk = hass.data[DOMAIN]
    async_add_entities([MyrtDeskHeight(desk.legs)])

class MyrtDeskHeight(NumberEntity):
    """MyrtDesk legs entity"""
    _name = "MyrtDesk Height"
    _available = False
    _value = 65
    _legs: MyrtDeskLegs = None

    def __init__(self, legs: MyrtDeskLegs):
        super().__init__()
        self._legs = legs

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement of desk height"""
        return LENGTH_CENTIMETERS

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return "myrt-desk-height"

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

    async def async_set_value(self, value: float) -> None:
        """Update the current value."""
        await self._legs.set_height(int(value * 10))
        self._value = value
        self._available = True
