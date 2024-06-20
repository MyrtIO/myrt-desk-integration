"""MyrtDesk API constants"""
from enum import Enum

from .types import DeskAction

API_PORT = 11011

class DeskFeature(Enum):
    """MyrtDesk features"""
    LIGHT = 1
    HEIGHT = 2

class LightAction(DeskAction):
    """MyrtDesk light actions"""
    SET_COLOR = 0
    GET_COLOR = 1
    SET_BRIGHTNESS = 2
    GET_BRIGHTNESS = 3
    SET_POWER = 4
    GET_POWER = 5
    SET_EFFECT = 6
    GET_EFFECT = 7

class HeightAction(DeskAction):
    """MyrtDesk height actions"""
    SET = 0
    GET = 1

class LightEffect(Enum):
    """Light effects"""
    NONE = 1
    RAINBOW = 2
