from pylatex import TikZDraw, TikZOptions
from .point import Point
from .text import Text


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
                 space: float = 1.5, text: Text = None):
        self._center = position.add_x(radius)
        self._radius = radius
        self._draw = draw
        self._fill = fill
        self._space = space
        self._text = text

        if isinstance(self._text, Text):
            self._text.define(position=self._center, size=(max(self._radius, 0.5), max(self._radius, 0.5)))

    def build(self, pic):
        circle = TikZDraw([self._center.tikz, 'circle'],
                          options=TikZOptions(radius=str(self._radius) + 'cm', draw=self._draw, fill=self._fill))
        pic.append(circle)

        if isinstance(self._text, Text):
            self._text.build(pic)
