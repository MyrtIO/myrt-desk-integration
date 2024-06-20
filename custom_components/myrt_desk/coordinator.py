"""MyrtDesk update coordinator"""
import asyncio
from logging import getLogger
from datetime import timedelta
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from async_timeout import timeout

from .const import UPDATE_INTERVAL
from .api import DeskAPI

_LOGGER = getLogger(__name__)

class MyrtDeskCoordinator(DataUpdateCoordinator):
    """MyrtDesk update coordinator"""

    _api: DeskAPI

    def __init__(self, hass, api: DeskAPI):
        """Initialize MyrtDesk coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="MyrtDesk API",
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self._api = api

    async def _async_update_data(self):
        try:
            async with timeout(UPDATE_INTERVAL):
                light = await self._api.get_light_state()
                height = await self._api.get_height()
                return {
                    "light": light,
                    "height": height
                }
        except (ValueError, asyncio.TimeoutError) as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
