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
from myrt_desk_api import MyrtDesk, discover
from .const import DOMAIN, CONF_ADDRESS

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_ADDRESS): cv.string
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

async def options_update_listener(
    hass: core.HomeAssistant, config_entry: config_entries.ConfigEntry
):
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)

async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Set up MyrtDesk entry."""
    hass.data.setdefault(DOMAIN, {})
    address = ""
    if CONF_ADDRESS in entry.data and entry.data[CONF_ADDRESS] is not None:
        address = entry.data[CONF_ADDRESS]
    else:
        address = await discover()
        if address is None:
            raise Exception("Discovery can't find MyrtDesk")
    desk = MyrtDesk(address)
    # Registers update listener to update config entry when options are updated.
    unsub_options_update_listener = entry.add_update_listener(options_update_listener)
    hass.data[DOMAIN][entry.entry_id] = {
        "unsub_options_update_listener": unsub_options_update_listener,
        "desk": desk
    }

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "light"))
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "number"))
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor"))
    return True
