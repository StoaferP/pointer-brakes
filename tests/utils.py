from __future__ import annotations

from math import sqrt

from pytweening import getLine


def distance_between_points(p1: tuple[int, int], p2: tuple[int, int]):
    return sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


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
