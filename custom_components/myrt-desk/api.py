from __future__ import annotations
from typing import Any, Callable, Dict, Optional
from aiohttp import ClientSession

class MyrtDeskAPI:
    def __init__(self, session: ClientSession, ip: str):
        self._ip = ip
        self._session = session

    def _url(self, path: str) -> str:
        return f"http://{self._ip}{path}"

    async def getValue(self, path: str):
        async with self._session.get(self._url(path)) as resp:
            return await resp.json()

    async def setValue(self, path: str, payload: dict):
            async with self._session.put(self._url(path), json=payload) as resp:
                return await resp.json()
