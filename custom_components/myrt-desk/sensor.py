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
    LIGHT_LUX
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.components.sensor import SensorEntity
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
    async_add_entities([MyrtDeskIlluminance(api)])

class MyrtDeskIlluminance(SensorEntity):
    _attr_name = "Myrt Desk Illuminance"
    _attr_native_unit_of_measurement = LIGHT_LUX
    _attr_device_class = SensorDeviceClass.ILLUMINANCE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _available = False
    _value = 0

    def __init__(self, api: MyrtDeskAPI):
        super().__init__()
        self._api = api

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return "myrt-desk-illuminance"

    @property
    def icon(self):
        return "mdi:sun-wireless"

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def native_value(self):
        return self._value

    async def async_update(self) -> None:
        """Update the current value."""
        # try:
        resp = await self._api.getValue("/sensors/illuminance")
        self._value = resp["value"]
        self._available = True
        # except ClientError:
        #     self._available = False
