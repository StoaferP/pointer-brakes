from __future__ import annotations

import copy
from dataclasses import dataclass

from pymatrix import Matrix, matrix

from pointer_brakes.exceptions import DeltaPositionInvalidError, DeltaTimeInvalidError, VelocityInvalidError


@dataclass(repr=True)
class State:
    timestamp: float | None = None
    touch_pos: tuple[int, int] | None = None


EMPTY_STATE = State()


class PointerMotionSim:
    # magnitude of acceleration due to braking (using during pointer rolling motion)
    a_braking: float

    # simulation state
    _state: State
    _last_state: State

    # initial velocity (using during pointer rolling motion)
    _v0: Matrix | None

    def __init__(self, a_braking: float):
        self.a_braking = a_braking
        self.state = State()
        self.last_state = State()
        self._v0 = None

    def tick(self, timestamp: float, touch_pos: tuple[int, int] | None = None):
        # if touch is idle and motion is stopped then do nothing
        if not touch_pos and not self.velocity:
            return

        # if touch is idle then update initial velocity
        if not touch_pos:
            self._v0 = self.velocity

        # update simulation state
        self.last_state = copy.deepcopy(self.state)
        self.state = copy.deepcopy(EMPTY_STATE)
        self.state.timestamp = timestamp

        # update touch data if present
        self.state.touch_pos = touch_pos if touch_pos else None

    @property
    def delta_time(self):
        if not self.state.timestamp or not self.last_state.timestamp:
            raise DeltaTimeInvalidError(self.last_state.timestamp, self.state.timestamp)

        return self.state.timestamp - self.last_state.timestamp

    @property
    def velocity(self):
        # if we have blank timestamps then motion is stopped
        if not self.last_state.timestamp and not self.state.timestamp:
            return None

        # handle transition from idle to touch motion
        if self.state.touch_pos and not self.last_state.touch_pos:
            return None

        # handle touch-driven motion
        if self.last_state.touch_pos and self.state.touch_pos:
            if not self.delta_position:
                raise DeltaPositionInvalidError(self.last_state.touch_pos, self.state.touch_pos)

            return self.delta_position.map(lambda x: x / self.delta_time)

        # handle pointer rolling motion
        if self._v0 and not self.state.touch_pos:
            # use standard accelerated motion calculation
            v_magnitude = self._v0.len() - self.a_braking * self.delta_time

            # if braking would reduce the velocity to 0 or less then stop motion
            if v_magnitude <= 0:
                self.stop_motion()
                return None

            return self._v0.dir().map(lambda x: x * v_magnitude)

        # this shouldn't be reachable!
        raise VelocityInvalidError

    def stop_motion(self):
        # reset the state to empty to indicate all motion is stopped
        self.last_state = copy.deepcopy(EMPTY_STATE)
        self.state = copy.deepcopy(EMPTY_STATE)
        self._v0 = None

    @property
    def delta_position(self):
        # if theres no touch data and no velocity we're not moving
        if (not self.state.touch_pos or not self.last_state.touch_pos) and not self.velocity:
            return None

        # handle touch-driven motion
        if self.state.touch_pos and self.last_state.touch_pos:
            return matrix(
                [
                    [
                        self.state.touch_pos[0] - self.last_state.touch_pos[0],
                        self.state.touch_pos[1] - self.last_state.touch_pos[1],
                    ]
                ]
            )

        # handle pointer rolling motion; use standard accelerated motion calculation
        if not self._v0:
            raise DeltaPositionInvalidError

        delta_pos_mag = self._v0.len() * self.delta_time + self.a_braking / 2 * self.delta_time**2
        return self._v0.dir().map(lambda x: x * delta_pos_mag)
