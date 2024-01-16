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
    """A simulation of pointer motion, including touch-driven and free rolling motions.

    Attributes:
        a_braking (float): The magnitude of acceleration caused by pointer brakes.

    Example:
        ```python
        sim_instance = PointerMotionSim(2.0)
        ```
    """

    # magnitude of acceleration due to braking (using during pointer rolling motion)
    a_braking: float

    # simulation state
    _state: State
    _last_state: State

    # initial velocity (using during pointer rolling motion)
    _v0: Matrix | None

    def __init__(self, a_braking: float) -> None:
        self.a_braking = a_braking
        self._state = State()
        self._last_state = State()
        self._v0 = None

    def tick(self, timestamp: float, touch_pos: tuple[int, int] | None = None) -> None:
        """Update the state of the PointerMotionSim

        This method updates the simulation state of the PointerMotionSim instance. When
        touch position is provided the pointer will be moved.  When the touch position,
        inevitably, goes idle then the simulation will continue moving until the
        pointer comes to rest due to braking.

        Args:
            timestamp (float): The timestamp at which the update occurs.
            touch_pos (tuple[int, int] | None): The current touch position as a tuple
                (x, y), or None if touch is idle.

        Example usage:
        ```python
        a_brakes = 1
        sim_instance = PointerMotionSim(a_brakes)
        current_timestamp = time.monotonic()
        current_touch_pos = (50, 50)
        sim_instance.tick(current_timestamp, current_touch_pos)
        ```
        """
        # if touch is idle and motion is stopped then do nothing
        if not touch_pos and not self.velocity:
            return

        # if touch is idle then update initial velocity
        if not touch_pos:
            self._v0 = self.velocity

        # update simulation state
        self._last_state = copy.deepcopy(self._state)
        self._state = copy.deepcopy(EMPTY_STATE)
        self._state.timestamp = timestamp

        # update touch data if present
        self._state.touch_pos = touch_pos if touch_pos else None

    @property
    def delta_time(self) -> float:
        """The time difference between the current state and the last state.

        This property calculates the delta time, representing the time elapsed between
        the current state and the last state in the simulation. It ensures that both
        timestamps are available; otherwise, it raises a DeltaTimeInvalidError.

        Returns:
            The time difference (delta time) between the current and last state
                timestamps.

        Raises:
            DeltaTimeInvalidError: If either the current state timestamp or the last state
                timestamp is not set.

        Example:
            ```python
            a_brakes = 1
            sim_instance = PointerMotionSim(a_brakes)
            sim_instance.tick(time.monotonic(), (50, 50))
            sim_instance.tick(time.monotonic(), (60, -30))
            time_difference = sim_instance.delta_time
            ```
        """
        if not self._state.timestamp or not self._last_state.timestamp:
            raise DeltaTimeInvalidError(self._last_state.timestamp, self._state.timestamp)

        return self._state.timestamp - self._last_state.timestamp

    @property
    def velocity(self) -> Matrix | None:
        """The current pointer velocity.

        This property handles various scenarios to determine the current velocity of
        the simulation. If there's touch-driven motion, it calculates velocity based on
        the change in position over time. For pointer rolling motion, it uses standard
        accelerated motion calculations where acceleration direction is opposite to
        velocity with magnitude of acceleration due to braking.

        Returns:
            The calculated velocity as a 2x1 Matrix instance or None if
                motion is stopped.

        Raises:
            DeltaPositionInvalidError: The change in is not valid during touch-driven
                motion.
            VelocityInvalidError: The p method encounters an unexpected condition.

        Example:
            ```python
            a_brakes = 1
            sim_instance = PointerMotionSim(a_brakes)
            sim_instance.tick(time.monotonic(), (30, 12))
            sim_instance.tick(time.monotonic(), (104, 23))
            current_velocity = sim_instance.velocity
            ```
        """
        # if we have blank timestamps then motion is stopped
        if not self._last_state.timestamp and not self._state.timestamp:
            return None

        # handle transition from idle to touch motion
        if self._state.touch_pos and not self._last_state.touch_pos:
            return None

        # handle touch-driven motion
        if self._last_state.touch_pos and self._state.touch_pos:
            if not self.delta_position:
                raise DeltaPositionInvalidError(self._last_state.touch_pos, self._state.touch_pos)

            return self.delta_position.map(lambda x: x / self.delta_time)

        # handle pointer rolling motion
        if self._v0 and not self._state.touch_pos:
            # use standard accelerated motion calculation
            v_magnitude = self._v0.len() - self.a_braking * self.delta_time

            # if braking would reduce the velocity to 0 or less then stop motion
            if v_magnitude <= 0:
                self.stop_motion()
                return None

            return self._v0.dir().map(lambda x: x * v_magnitude)

        raise VelocityInvalidError

    def stop_motion(self) -> None:
        """Stop all motion in the simulation

        This method resets the simulation state and initial velocity to indicate that
        all motion has stopped.

        Example usage:
            ```python
            a_brakes = 1
            sim_instance = PointerMotionSim(a_brakes)
            sim_instance.tick(time.monotonic(), (15, -75))
            sim_instance.tick(time.monotonic(), (-83, 11))
            sim_instance.stop_motion()
            ```
        """
        # reset the state to empty to indicate all motion is stopped
        self._last_state = copy.deepcopy(EMPTY_STATE)
        self._state = copy.deepcopy(EMPTY_STATE)
        self._v0 = None

    @property
    def delta_position(self) -> Matrix | None:
        """The change in position between the last two state ticks.

        For touch-driven motion, it simply calculates the change in position between
        the current and last touch positions. For pointer rolling motion, it uses
        standard accelerated motion calculations where acceleration direction is
        opposite to velocity with magnitude of acceleration due to braking.

        Returns:
            The 2x1 Matrix representing the change in position from last
                state tick to the current state tick.

        Raises:
            DeltaPositionInvalidError: If the delta position cannot be determined.

        Example:
            ```python
            a_brakes = 1
            sim_instance = PointerMotionSim(a_brakes)
            sim_instance.tick(time.monotonic(), (-52, -5))
            sim_instance.tick(time.monotonic(), (21, -92))
            change_in_position = sim_instance.delta_position
            ```
        """
        # if theres no touch data and no velocity we're not moving
        if (not self._state.touch_pos or not self._last_state.touch_pos) and not self.velocity:
            return None

        # handle touch-driven motion
        if self._state.touch_pos and self._last_state.touch_pos:
            return matrix(
                [
                    [
                        self._state.touch_pos[0] - self._last_state.touch_pos[0],
                        self._state.touch_pos[1] - self._last_state.touch_pos[1],
                    ]
                ]
            )

        # handle pointer rolling motion; use standard accelerated motion calculation
        if not self._v0:
            raise DeltaPositionInvalidError

        delta_pos_mag = self._v0.len() * self.delta_time + self.a_braking / 2 * self.delta_time**2
        return self._v0.dir().map(lambda x: x * delta_pos_mag)
