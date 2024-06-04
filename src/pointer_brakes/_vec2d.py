from __future__ import annotations

import math


class Vec2D:
    x: float
    y: float

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def len(self) -> float:
        return math.sqrt(self.x**2 + self.y**2)

    def dir(self) -> Vec2D:
        if self.len() == 0:
            return Vec2D(0, 0)
        return Vec2D(self.x / self.len(), self.y / self.len())

    def __truediv__(self, other) -> Vec2D:
        return Vec2D(self.x / other, self.y / other)

    def __mul__(self, other) -> Vec2D:
        return Vec2D(self.x * other, self.y * other)
