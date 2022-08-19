"""Desk Height integration."""
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
from homeassistant.helpers.discovery import async_load_platform
import voluptuous as vol

from .api import MyrtDeskAPI

from .const import (
    CONF_ADDRESS,
    DOMAIN,
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_ADDRESS): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass: HomeAssistantType, config: ConfigType) -> None:
    """Set up intergration."""
    session = async_get_clientsession(hass)
    api = MyrtDeskAPI(session, config[DOMAIN][CONF_ADDRESS])
    hass.data[DOMAIN] = api
    hass.async_create_task(async_load_platform(hass, "number", DOMAIN, {}, config))
    hass.async_create_task(async_load_platform(hass, "light", DOMAIN, {}, config))
    return True
