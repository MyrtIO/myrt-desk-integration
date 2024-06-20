"""Desk Height integration."""
from homeassistant import config_entries, core
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .api import connect_desk
from .coordinator import MyrtDeskCoordinator
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
        address = "MyrtDesk.local"
    api = await connect_desk(address)

    coordinator = MyrtDeskCoordinator(hass, api)
    # Registers update listener to update config entry when options are updated.
    unsub_options_update_listener = entry.add_update_listener(options_update_listener)
    hass.data[DOMAIN][entry.entry_id] = {
        "unsub_options_update_listener": unsub_options_update_listener,
        "api": api,
        "coordinator": coordinator
    }

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "light"))
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "number"))
    return True
