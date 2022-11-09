"""MyrtDesk light integration"""
from datetime import timedelta
import logging
from typing import Any, Callable, List, Optional
from aiohttp import ClientError
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ATTR_HS_COLOR,
    ATTR_EFFECT,
    COLOR_MODE_HS,
    COLOR_MODE_COLOR_TEMP,
    LightEntity,
    SUPPORT_EFFECT
)
import homeassistant.util.color as color_util
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
from myrt_desk_api.backlight import MyrtDeskBacklight, Effect

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=5)

effects: List[str] = []
for effect in Effect:
    effects.append(effect.name.lower().capitalize())

# pylint: disable-next=unused-argument
async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up desk height."""
    desk = hass.data[DOMAIN]
    async_add_entities([MyrtDeskLight(desk.backlight)])

class MyrtDeskLight(LightEntity):
    """MyrtDesk backlight entity"""
    _backlight: MyrtDeskBacklight = None
    _is_on: bool = False
    _rgb: tuple[int, int, int] = (255, 255, 255)
    _temperature = 0
    _brightness: int = 255
    _attr_supported_features = SUPPORT_EFFECT
    _attr_effect_list = effects
    _attr_min_mireds = 166
    _attr_effect = effects[0]
    _attr_max_mireds = 400
    _attr_name = "MyrtDesk Backlight"
    _attr_color_mode = COLOR_MODE_HS
    _attr_available = False

    def __init__(self, backlight: MyrtDeskBacklight):
        super().__init__()
        self._backlight = backlight
        self._mireds_range_max = self._attr_max_mireds - self._attr_min_mireds

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
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._is_on

    @property
    def supported_color_modes(self) -> int:
        """Flag supported color modes."""
        return {COLOR_MODE_HS, COLOR_MODE_COLOR_TEMP}

    @property
    def hs_color(self) -> tuple[int, int, int]:
        """Return the color of the device."""
        return color_util.color_RGB_to_hs(*self._rgb)

    async def async_update(self) -> None:
        """Update the current value."""
        try:
            state = await self._backlight.read_state()
            self._brightness = state["brightness"]
            self._is_on = state["enabled"]
            self._rgb = state["color"]
            self._attr_color_mode = COLOR_MODE_HS if state["mode"] == 0 else COLOR_MODE_COLOR_TEMP
            self._attr_effect = Effect(state["effect"]).name.lower().capitalize()
            self._temperature = self._byte_to_mireds(state["warmness"])
            self._attr_available = True
        except ClientError:
            self._attr_available = False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Update the current value."""
        try:
            if not self._is_on:
                await self._backlight.set_power(True)
                self._is_on = True

            if ATTR_EFFECT in kwargs:
                await self._backlight.set_effect(effects.index(kwargs[ATTR_EFFECT]))
                return
            else:
                await self._backlight.set_effect(0)

            if ATTR_BRIGHTNESS in kwargs and kwargs[ATTR_BRIGHTNESS] != self._brightness:
                self._brightness = kwargs[ATTR_BRIGHTNESS]
                await self._backlight.set_brightness(self._brightness)
            if ATTR_COLOR_TEMP in kwargs and kwargs[ATTR_COLOR_TEMP] != self._temperature:
                self._temperature = kwargs[ATTR_COLOR_TEMP]
                self._attr_color_mode = COLOR_MODE_COLOR_TEMP
                await self._backlight.set_white(self._mireds_to_byte(self._temperature))
            elif ATTR_HS_COLOR in kwargs and not self._is_same_color(*kwargs[ATTR_HS_COLOR]):
                self._rgb = color_util.color_hs_to_RGB(*kwargs[ATTR_HS_COLOR])
                self._attr_color_mode = COLOR_MODE_HS
                await self._backlight.set_color(self._rgb)
            self._attr_available = True
        except ClientError:
            self._attr_available = False

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        try:
            await self._backlight.set_power(False)
            self._is_on = False
            self._attr_available = True
        except ClientError:
            self._attr_available = False

    def _is_same_color(self, hue: float, saturation: float):
        return self._rgb != color_util.color_hs_to_RGB(hue, saturation)

    def _mireds_to_byte(self, mireds: int) -> int:
        ranged_temp = mireds - self._attr_min_mireds
        percent = ranged_temp / self._mireds_range_max
        return int(255 * percent)

    def _byte_to_mireds(self, byte_temp: int) -> int:
        percent = byte_temp / 255
        return int(percent *  self._mireds_range_max) + self._attr_min_mireds
