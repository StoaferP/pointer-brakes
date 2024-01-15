from __future__ import annotations

import time
from math import isclose

import pytest

from pointer_brakes import PointerMotionSim

from .utils import (
    distance_between_points,
    get_delta_time,
    prep_sim_for_rolling,
    swipe_idle,
    swipe_left,
    swipe_right,
    swipe_swirl,
)


# test touch motion that interrupts rolling motion
def test_touch_interrupts_rolling():
    # prep sim for pointer rolling
    a_brake = 5
    sim = PointerMotionSim(a_brake)
    fake_t = prep_sim_for_rolling(sim, (-32, 15), (-28, 23), 100)

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


# rolling motion stops when new velocity magnitude drops below (or at) 0
def test_rolling_motion_stops_eventually():
    # prep sim for rolling
    a_brake = 2
    sim = PointerMotionSim(a_brake)
    v_prep = 20
    fake_t = prep_sim_for_rolling(sim, (-120, -84), (-23, -39), v_prep)

    # run sim with touch idle until we expect pointer motion to stop
    delta_time = v_prep / a_brake  # found by solving v=v0-a*t when v=0
    sim.tick(fake_t + delta_time + 0.1)  # fudge 100ms because floating point accuracy

    # assert motion is stopped
    assert sim.velocity is None


# rolling motion correctly calculates velocity and delta position
def test_rolling_motion_correct_calculations():
    # prep sim for rolling
    a_brake = 7
    sim = PointerMotionSim(a_brake)
    v_prep = 48
    fake_t = prep_sim_for_rolling(sim, (12, 3), (-9, 25), v_prep)

    # run sim with touch idle to so some rolling
    delta_time = 2
    sim.tick(fake_t + delta_time)

    # assert velocity and delta_position are calculated as we expect
    assert sim.velocity
    assert isclose(sim.velocity.len(), v_prep - a_brake * delta_time)
    assert sim.delta_position
    # lets tolerate 1e-06 cuz floating point accuracy
    assert isclose(sim.velocity.len(), v_prep * delta_time - a_brake / 2 * delta_time**2, rel_tol=6)


# when motion is stopped velocity and delta_position are None
def test_motion_stopped_then_no_calculations():
    # prep for rolling
    sim = PointerMotionSim(13)
    _ = prep_sim_for_rolling(sim, (23, -32), (2, -1), 2)

    # manually stop motion
    sim.stop_motion()

    # assert velocity and delta_postion are None
    assert sim.velocity is None
    assert sim.delta_position is None


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
