import time

import pytest

from pointer_brakes import PointerMotionSim

from .utils import distance_between_points, swipe_left, swipe_right, swipe_swirl

# test touch motion that interrupts rolling motion


# test touch swipe
@pytest.mark.parametrize("swipe", [swipe_right, swipe_left, swipe_swirl])
# test simple touch-driven motion (ie. a finger swipe with optional leading idle)
@pytest.mark.parametrize("swipe", [swipe_right, swipe_left, swipe_swirl, swipe_idle])
@pytest.mark.parametrize("idle_before", [lambda: [], swipe_idle])
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
