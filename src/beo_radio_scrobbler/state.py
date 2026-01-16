import asyncio
from collections import deque


class LoveState:
    _love_detection_deque = deque(maxlen=15)
    _base_volume = None
    _love_detection_task = None

love_state = LoveState()
