from __future__ import annotations

import copy
from dataclasses import dataclass

from pymatrix import matrix


@dataclass(repr=True)
class State:
    timestamp: float | None = None
    touch_pos: tuple[int, int] | None = None


EMPTY_STATE = State()


class PointerMotionSim:
    state = State()
    last_state = State()

    def tick(self, timestamp: float, touch_pos: tuple[int, int] | None = None):
        self.last_state = copy.deepcopy(self.state)
        self.state = copy.deepcopy(EMPTY_STATE)
        self.state.timestamp = timestamp

        if not touch_pos:
            return

        self.state.touch_pos = touch_pos

    @property
    def delta_position(self):
        if not self.state.touch_pos or not self.last_state.touch_pos:
            return None

        return matrix(
            [
                [
                    self.state.touch_pos[0] - self.last_state.touch_pos[0],
                    self.state.touch_pos[1] - self.last_state.touch_pos[1],
                ]
            ]
        )
