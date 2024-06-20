"""MyrtDesk API types"""
from enum import Enum
from typing import TypedDict

DeskAction = Enum

class LightState(TypedDict):
    """Light state dictionary"""
    power: bool
    brightness: int
    color: tuple[int, int, int]
    effect: int
