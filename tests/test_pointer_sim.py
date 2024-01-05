import time

import pytest

from pointer_brakes import PointerMotionSim

from .utils import distance_between_points, swipe_left, swipe_right, swipe_swirl

# a list of Nones for indicating touch input is idle
TOUCH_IDLE = 100 * [None]


# test touch swipe
@pytest.mark.parametrize("swipe", [swipe_right, swipe_left, swipe_swirl])
@pytest.mark.parametrize("idle_before", [[], TOUCH_IDLE])
@pytest.mark.parametrize("idle_after", [[], TOUCH_IDLE])
def test_touch_swipe(swipe, idle_before, idle_after):
    sim = PointerMotionSim()

    touch_data = idle_before + swipe() + idle_after
    for i in range(len(touch_data)):
        # do tick
        sim.tick(time.monotonic(), touch_data[i])

        # assert delta_pos is as expected
        if i == 0 or not touch_data[i] or not touch_data[i - 1]:
            assert not sim.delta_position
            continue

        assert sim.delta_position
        assert sim.delta_position.len() == distance_between_points(touch_data[i - 1], touch_data[i])
