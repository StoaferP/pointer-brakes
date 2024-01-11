from __future__ import annotations

import time
from math import hypot
from typing import TYPE_CHECKING

from pytweening import getLine

if TYPE_CHECKING:
    from pointer_brakes import PointerMotionSim


def prep_sim_for_rolling(sim: PointerMotionSim, p1: tuple[int, int], p2: tuple[int, int], v12: float):
    delta_time = get_delta_time(p1, p2, v12)

    # run sim with contrived data
    t0 = time.monotonic()
    sim.tick(t0, p1)
    sim.tick(t0 + delta_time, p2)

    return t0 + delta_time


def get_delta_time(p1: tuple[int, int], p2: tuple[int, int], v12: float):
    # v = distance / delta_time
    # delta_time = distance / v
    return hypot(p2[0] - p1[0], p2[1] - p1[1]) / v12


def distance_between_points(p1: tuple[int, int], p2: tuple[int, int]):
    return hypot(p2[0] - p1[0], p2[1] - p1[1])


def swipe_idle():
    return 100 * [None]


def swipe_left():
    start = (61, 10)
    end = (start[0] - 99, start[1] - 12)

    return swipe(start, end)


def swipe_right():
    start = (-55, 3)
    end = (start[0] + 103, start[1] - 5)

    return swipe(start, end)


def swipe_swirl():
    points = [(-49, 1), (1, 52), (58, -3), (-2, -68), (14, 76), (89, -22)]

    touch_data = []
    for i in range(len(points)):
        if i == 0:
            continue

        touch_data += swipe(points[i - 1], points[i])

    return touch_data


def swipe(p1: tuple[int, int], p2: tuple[int, int]):
    return getLine(p1[0], p1[1], p2[0], p2[1])
