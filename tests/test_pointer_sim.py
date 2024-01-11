from __future__ import annotations

import time
from math import isclose
from typing import Callable

import pytest

from pointer_brakes import PointerMotionSim

from .utils import distance_between_points, get_delta_time, swipe_idle, swipe_left, swipe_right, swipe_swirl


# test touch motion that interrupts rolling motion
def test_touch_interrupts_rolling():
    # start rolling motion
    a_brake = 1
    sim = PointerMotionSim(a_brake)

    # pick two arbitrary points and find the delta time which would result in a certain velocity
    v12 = 4
    p1 = (-32, 15)
    p2 = (-28, 23)
    t12 = get_delta_time(p1, p2, v12)

    # run sim with contrived data
    fake_t = time.monotonic()
    sim.tick(fake_t, p1)
    fake_t += t12
    sim.tick(fake_t, p2)

    # run sim with touch idle to start pointer rolling motion
    fake_t += 1
    sim.tick(fake_t)

    # interrupt with touch data
    p3 = (-4, 84)
    p4 = (-20, 90)
    v34 = 7
    t34 = get_delta_time(p3, p4, v34)
    fake_t += 0.2
    sim.tick(fake_t, p3)
    fake_t += t34
    sim.tick(fake_t, p4)

    # assert velocity is expected
    assert sim.velocity
    assert isclose(sim.velocity.len(), v34)

    # assert delta position is expected
    assert sim.delta_position
    assert isclose(sim.delta_position.len(), distance_between_points(p3, p4))


# test rolling motion (motion which continues after touch-motion, for example, a finger swipe then idle)
@pytest.mark.parametrize("swipe", [swipe_right, swipe_left, swipe_swirl])
def test_touch_motion_then_idle(swipe: Callable[[], list[tuple[int, int]]]):
    # instantiate sim while specifying braking acceleration
    a_brake = 1
    sim = PointerMotionSim(a_brake)

    # construct touch data
    touch_data = swipe()
    final_pos = touch_data.pop()

    # tick through touch data
    for pos in touch_data:
        sim.tick(time.monotonic(), pos)

    # ensure final pointer velocity is above braking acceleration
    final_v = 4
    delta_time = get_delta_time(touch_data[-1], final_pos, final_v)
    time.sleep(delta_time)
    sim.tick(time.monotonic(), final_pos)

    # tick through idle data
    t_idle = time.monotonic()
    for pos in swipe_idle():
        v0 = sim.velocity

        # simulate a slow (embedded?) device by adding 20ms each tick
        t_idle += 0.2
        sim.tick(t_idle, pos)

        # we don't check anything if motion is stopped
        if sim.state.timestamp is None or sim.last_state.timestamp is None:
            continue

        # calculate delta time
        delta_time = sim.state.timestamp - sim.last_state.timestamp

        # assert velocity matches our expectation
        v_mag = v0.len() - a_brake * delta_time if v0 else 0

        # we expect None if velocity magnitude would have stopped or if motion is halted
        if v0 is None or v_mag <= 0:
            assert sim.velocity is None

        else:
            assert sim.velocity is not None
            assert isclose(sim.velocity.len(), v_mag)

        # assert delta pos matches our expectation

        # if motion is halted we expect None
        if sim.velocity is None:
            assert sim.delta_position is None
        # otherwise we expect the normal accelerated motion calculation
        else:
            assert sim.delta_position is not None
            assert v0 is not None
            assert isclose(sim.delta_position.len(), v0.len() * delta_time - a_brake * delta_time**2, rel_tol=6)


# test simple touch-driven motion (ie. a finger swipe with optional leading idle)
@pytest.mark.parametrize("swipe", [swipe_right, swipe_left, swipe_swirl, swipe_idle])
@pytest.mark.parametrize("idle_before", [list, swipe_idle])
def test_idle_then_touch_motion(swipe, idle_before):
    sim = PointerMotionSim(31.337)

    touch_data = idle_before() + swipe()
    for i in range(len(touch_data)):
        # do tick
        sim.tick(time.monotonic(), touch_data[i])

        # assert delta_pos is as expected
        if i == 0 or not touch_data[i] or not touch_data[i - 1]:
            assert sim.delta_position is None
            continue

        assert sim.delta_position is not None
        assert sim.delta_position.len() == distance_between_points(touch_data[i - 1], touch_data[i])
