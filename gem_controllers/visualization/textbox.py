from pylatex import TikZDraw, TikZOptions
from .point import Point
from .text import Text


class TextBox:

    @property
    def right(self):
        return self._position.add_x(self._size_x / 2, 'east')

    @property
    def left(self):
        return self._position.add_x(-self._size_x / 2, 'west')

    @property
    def top(self):
        return self._position.add_y(self._size_y / 2, 'north')

    @property
    def bottom(self):
        return self._position.add_y(-self._size_y / 2, 'south')

    @property
    def top_left(self):
        return self._position.add(-self._size_x / 2, self._size_y / 2)

    @property
    def bottom_right(self):
        return self._position.add(self._size_x / 2, -self._size_y / 2)

    @property
    def end(self):
        return self.right.add_x(self._space)

    def __init__(self, position: Point, size: tuple = (2.5, 1.5), text: Text = None, fill: str = 'white',
                 draw: str = 'black', space: float = 1.5):
        self._position = position.add_x(size[0] / 2)
        (self._size_x, self._size_y) = size
        self._fill = fill
        self._draw = draw
        self._space = space

        self._text = text
        if isinstance(self._text, Text):
            self._text.define(position=Point(self._position.x, self._position.y), size=size)

    def build(self, pic):
        box = TikZDraw([self.top_left.tikz, 'rectangle', self.bottom_right.tikz],
                       TikZOptions(draw=self._draw, fill=self._fill))
        pic.append(box)
        if isinstance(self._text, Text):
            self._text.build(pic)
