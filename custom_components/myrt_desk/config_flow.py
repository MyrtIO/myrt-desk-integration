"""MyrtDesk Config flow"""
from typing import Any, Dict, Optional

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from myrt_desk_api.discover import is_desk

from .const import CONF_ADDRESS, DOMAIN

DESK_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_ADDRESS): cv.string
    }
)

OPTIONS_SHCEMA = vol.Schema({vol.Optional(CONF_NAME, default="foo"): cv.string})


async def validate_address(address: str) -> None:
    """Validates a MyrtDesk address by trying to connect.
    Raises a ValueError if the path is invalid.
    """
    if not await is_desk(address):
        raise ValueError

class MyrtDeskConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """MyrtDesk config flow."""

    data: Optional[Dict[str, Any]]

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Invoked when a user initiates a flow via the user interface."""
        errors: Dict[str, str] = {}
        if user_input is not None:
            try:
                if CONF_ADDRESS in user_input and user_input[CONF_ADDRESS] is not None:
                    await validate_address(user_input[CONF_ADDRESS])
            except ValueError:
                errors["base"] = "address_error"
            if not errors:
                self.data = user_input
                return self.async_create_entry(title="MyrtDesk", data=self.data)

        return self.async_show_form(
            step_id="user", data_schema=DESK_SCHEMA, errors=errors
        )
