from pylatex import TikZNode, TikZDraw, TikZCoordinate, TikZOptions
from .point import Point


class Circle:

    @property
    def left(self):
        return Point(self._center.x - self._radius, self._center.y, 'west')

    @property
    def right(self):
        return Point(self._center.x + self._radius, self._center.y, 'east')

    @property
    def top(self):
        return Point(self._center.x, self._center.y + self._radius, 'north')

    @property
    def bottom(self):
        return Point(self._center.x, self._center.y - self._radius, 'south')

    @property
    def end(self):
        return self.right.add_x(self._space)

    def __init__(self, position: Point, radius: float = 1, draw: str = 'black', fill: str = 'white',
                 space: float = 1.5):
        self._center = position.add_x(radius)
        self._radius = radius
        self._draw = draw
        self._fill = fill
        self._space = space

    def build(self, pic):
        circle = TikZDraw([self._center.tikz, 'circle'],
                          options=TikZOptions(radius=str(self._radius) + 'cm', draw=self._draw, fill=self._fill))
        pic.append(circle)
