from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class Vec2D:
    x: float
    y: float

    def len(self) -> float:
        return math.sqrt(self.x**2 + self.y**2)

    def dir(self) -> Vec2D:
        return Vec2D(self.x / self.len(), self.y / self.len())

    def __truediv__(self, other) -> Vec2D:
        return Vec2D(self.x / other, self.y / other)

    def __mul__(self, other) -> Vec2D:
        return Vec2D(self.x * other, self.y * other)
