"""MyrtDesk API wrapper"""
from myrtio import (
    MyrtIOTransport,
    Message,
    from_byte_pair,
    split_byte_pair,
)
from .constants import API_PORT, DeskFeature, LightAction, HeightAction, LightEffect
from .types import LightState, DeskAction
from myrtio_udp import connect_udp

class DeskAPI:
    """API wrapper for MyrtDesk API features"""
    _transport: MyrtIOTransport = None

    def __init__(self, transport: MyrtIOTransport):
        self._transport = transport

    async def get_height(self) -> int:
        """Reads height value"""
        resp = await self._get_state(DeskFeature.HEIGHT, HeightAction.GET)
        return from_byte_pair(resp[0], resp[1])

    async def set_height(self, height: int):
        """Sets desk's height"""
        await self._set_state(
            feature=DeskFeature.HEIGHT,
            action=HeightAction.SET,
            payload=split_byte_pair(height)
        )

    async def set_color(self, color: tuple[int, int, int]):
        """Sets light's color"""
        await self._set_state(
            feature=DeskFeature.LIGHT,
            action=LightAction.SET_COLOR,
            payload=[*color]
        )

    async def set_brightness(self, brightness: int):
        """Sets light's brightness"""
        await self._set_state(
            feature=DeskFeature.LIGHT,
            action=LightAction.SET_BRIGHTNESS,
            payload=[brightness]
        )

    async def set_power(self, power: bool):
        """Sets light's power"""
        await self._set_state(
            feature=DeskFeature.LIGHT,
            action=LightAction.SET_POWER,
            payload=[int(power)]
        )

    async def set_effect(self, effect: LightEffect):
        """Sets light's effect"""
        await self._set_state(
            feature=DeskFeature.LIGHT,
            action=LightAction.SET_EFFECT,
            payload=[effect.value]
        )

    async def get_light_state(self) -> LightState:
        """Reads light desk's state"""
        power_resp = await self._get_state(DeskFeature.LIGHT, LightAction.GET_POWER)
        brightness_resp = await self._get_state(DeskFeature.LIGHT, LightAction.GET_BRIGHTNESS)
        color_resp = await self._get_state(DeskFeature.LIGHT, LightAction.GET_COLOR)
        effect_resp = await self._get_state(DeskFeature.LIGHT, LightAction.GET_EFFECT)

        return LightState(
            power=power_resp[0] == 1,
            brightness=brightness_resp[0],
            color=[color_resp[0], color_resp[1], color_resp[2]],
            effect=effect_resp[0]
        )

    async def _get_state(self, feature: DeskFeature, action: DeskAction) -> bytes:
        """Reads state value"""
        resp = await self._transport.run_action(Message(
            feature=feature.value,
            action=action.value,
        ))
        if not resp.is_successful:
            raise ValueError(f"Request error: {feature} {action}")
        return resp.payload_without_status

    async def _set_state(self,
                         feature: DeskFeature,
                         action: DeskAction,
                         payload: list[int]) -> None:
        """Sets state value"""
        await self._transport.run_action(Message(
            feature=feature.value,
            action=action.value,
            payload=payload
        ))

async def connect_desk(address: str) -> DeskAPI:
    """Connects to MyrtDesk"""
    stream = await connect_udp(address, API_PORT)
    return DeskAPI(stream)
