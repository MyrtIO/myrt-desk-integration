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
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ATTR_HS_COLOR,
    ATTR_EFFECT,
    COLOR_MODE_HS,
    COLOR_MODE_COLOR_TEMP,
    LightEntity,
    SUPPORT_EFFECT,
    SUPPORT_TRANSITION,
    ATTR_TRANSITION
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
import homeassistant.util.color as color_util
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
import voluptuous as vol

from .const import (
    DATA_API,
    DOMAIN,
)

from .api import (
    MyrtDeskAPI
)

from .light_effects import effects

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
    async_add_entities([MyrtDeskLight(api)])

class MyrtDeskLight(LightEntity):
    _is_on: bool = False
    _available: bool = False
    _rgb: tuple[int, int, int] = (255, 255, 255)
    _temperature = 0
    _brightness: int = 255
    _attr_supported_features = SUPPORT_EFFECT | SUPPORT_TRANSITION
    _attr_effect_list = effects
    _attr_min_mireds = 166
    _attr_max_mireds = 400
    _mode = COLOR_MODE_HS


    def __init__(self, api: MyrtDeskAPI):
        super().__init__()
        self._api = api
        self._name = "Myrt Desk Light"
        self._available = False
        self._mireds_range_max = self._attr_max_mireds - self._attr_min_mireds

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return "myrt-desk-light"

    @property
    def icon(self):
        return "mdi:led-strip-variant"

    @property
    def brightness(self) -> int:
        """Return the brightness of the device."""
        return self._brightness

    @property
    def color_mode(self):
        """Return the color mode of the device."""
        return self._mode

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._is_on

    @property
    def supported_color_modes(self) -> int:
        """Flag supported color modes."""
        return {COLOR_MODE_HS, COLOR_MODE_COLOR_TEMP}

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def hs_color(self) -> tuple[int, int, int]:
        """Return the color of the device."""
        return color_util.color_RGB_to_hs(*self._rgb)

    async def async_update(self) -> None:
        """Update the current value."""
        try:
            resp = await self._api.getValue("/backlight")
            self._brightness = resp["brightness"]
            self._is_on = resp["enabled"]
            self._rgb = tuple(resp["color"])
            self._temperature = self.byte_to_mireds(resp["temperature"])
            self._available = True
        except ClientError:
            self._available = False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Update the current value."""
        try:
            if ATTR_EFFECT in kwargs:
                await self._api.setValue("/backlight/effects", {
                    "active": effects.index(kwargs[ATTR_EFFECT])
                })
                return
            request = {}
            if ATTR_BRIGHTNESS in kwargs and kwargs[ATTR_BRIGHTNESS] != self._brightness:
                self._brightness = kwargs[ATTR_BRIGHTNESS]
                request["brightness"] = self._brightness
            if ATTR_COLOR_TEMP in kwargs and kwargs[ATTR_COLOR_TEMP] != self._temperature:
                self._temperature = kwargs[ATTR_COLOR_TEMP]
                self._mode = COLOR_MODE_COLOR_TEMP
                request["temperature"] = self.mireds_to_byte(self._temperature)
            elif ATTR_HS_COLOR in kwargs and self._rgb != color_util.color_hs_to_RGB(*kwargs[ATTR_HS_COLOR]):
                self._rgb = color_util.color_hs_to_RGB(*kwargs[ATTR_HS_COLOR])
                self._mode = COLOR_MODE_HS
                request["color"] = list(self._rgb)

            if self._is_on:
                await self._api.setValue("/backlight/color", request)
            else:
                req = {"brightness": self._brightness}
                if self._mode == COLOR_MODE_HS:
                    req["color"] = list(self._rgb)
                else:
                    req["temperature"] = self._temperature
                await self._api.setValue("/backlight/color", req)
                self._is_on = True
            self._available = True
        except ClientError:
            self._available = False

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        try:
            await self._api.setValue("/backlight/power", {
                "enabled": False
            })
            self._is_on = False
            self._available = True
        except ClientError:
            self._available = False

    def mireds_to_byte(self, mireds: int) -> int:
        ranged_temp = mireds - self._attr_min_mireds
        percent = ranged_temp / self._mireds_range_max
        return int(255 * percent)

    def byte_to_mireds(self, byte_temp: int) -> int:
        percent = byte_temp / 255
        return int(percent *  self._mireds_range_max) + self._attr_min_mireds
