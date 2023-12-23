"""MyrtDesk update coordinator"""
from logging import getLogger
from datetime import timedelta
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from async_timeout import timeout
from asyncio import TimeoutError
from aiohttp import ClientError
from myrt_desk_api import MyrtDesk
from .const import UPDATE_INTERVAL

_LOGGER = getLogger(__name__)

class MyrtDeskCoordinator(DataUpdateCoordinator):
    """MyrtDesk update coordinator"""

    def __init__(self, hass, desk: MyrtDesk):
        """Initialize MyrtDesk coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="MyrtDesk API",
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.desk = desk

    async def _async_update_data(self):
        try:
            async with timeout(UPDATE_INTERVAL):
                light = await self.desk.backlight.read_state()
                heap = await self.desk.system.read_heap()
                height = await self.desk.legs.read_height()
                return {
                    "light": light,
                    "heap": heap,
                    "height": height
                }
        except (ClientError, ValueError, TimeoutError) as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
