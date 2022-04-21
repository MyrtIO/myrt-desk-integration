from datetime import timedelta
import logging
from typing import Any, Callable, Dict, Optional
from aiohttp import ClientError

from homeassistant import config_entries, core
from homeassistant.const import (
    ATTR_NAME,
    CONF_ACCESS_TOKEN,
    CONF_NAME,
    CONF_PATH,
    CONF_URL,
    LENGTH_CENTIMETERS
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
import homeassistant.components.number as number
from homeassistant.components.number import NumberEntity
import voluptuous as vol

from .const import (
    DATA_API,
    DOMAIN,
)

from .api import (
    MyrtDeskAPI
)

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=5)

async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up desk height."""
    api = hass.data[DOMAIN]
    async_add_entities([MyrtDeskHeight(api)])

class MyrtDeskHeight(NumberEntity):
    _name = "Myrt Desk Height"
    _available = False
    _value = 65

    def __init__(self, api: MyrtDeskAPI):
        super().__init__()
        self._api = api

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def unit_of_measurement(self):
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
    def value(self):
        return self._value

    @property
    def min_value(self):
        return 65

    @property
    def max_value(self):
        return 125

    async def async_update(self) -> None:
        """Update the current value."""
        try:
            resp = await self._api.getValue("/legs")
            self._value = resp["height"] / 10
            self._available = True
        except ClientError:
            self._available = False

    async def async_set_value(self, value: float) -> None:
        """Update the current value."""
        try:
            await self._api.setValue("/legs", {
                "height": int(value * 10)
            })
            self._value = value
            self._available = True
        except ClientError:
            self._available = False
