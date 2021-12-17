from pylatex import TikZNode, TikZDraw, TikZCoordinate, TikZOptions
from .point import Point
from .connection import Connection
from .text import Text


class TextBox:

    @property
    def right(self):
        return Point(self._right, self._pos_y, 'east')

    @property
    def left(self):
        return Point(self._left, self._pos_y, 'west')

    @property
    def top(self):
        return Point(self._pos_x, self._top, 'north')

    @property
    def bottom(self):
        return Point(self._pos_x, self._bottom, 'south')

    @property
    def top_left(self):
        return Point(self._left, self._top)

    @property
    def bottom_right(self):
        return Point(self._right, self._bottom)

    @property
    def end(self):
        return self.right.add_x(self._space)

    def __init__(self, position: Point, size: tuple = (2.5, 1.5), text: Text = None, fill: str = 'white',
                 draw: str = 'black', space: float = 1.5):
        (self._pos_x, self._pos_y) = (position[0] + size[0] / 2, position[1])
        (self._size_x, self._size_y) = size
        self._fill = fill
        self._draw = draw
        self._space = space

        self._right = self._pos_x + self._size_x / 2
        self._left = self._pos_x - self._size_x / 2
        self._top = self._pos_y + self._size_y / 2
        self._bottom = self._pos_y - self._size_y / 2

        self._text = text
        self._text.define(position=Point(self._pos_x, self._pos_y), size=size)

    def build(self, pic):
        box = TikZDraw([self.top_left.tikz, 'rectangle', self.bottom_right.tikz],
                       TikZOptions(draw=self._draw, fill=self._fill))
        pic.append(box)
        if self._text is not None:
            self._text.build(pic)

    @staticmethod
    def connect(box1, box2) -> Connection:

        if box1._right < box2._left:
            start = box1.right
            inter_1 = Point(box1._right + (box2._left - box1._right) / 2, box1._pos_y)
            inter_2 = Point(box1._right + (box2._left - box1._right) / 2, box2._pos_y)
            end = box2.left

        elif box1._left > box2._right:
            start = box1.left
            inter_1 = Point(box1._right + (box2._left - box1._right) / 2, box1._pos_y)
            inter_2 = Point(box1._right + (box2._left - box1._right) / 2, box2._pos_y)
            end = box2.right

        elif box1._top < box2._bottom:
            start = box1.top
            inter_1 = Point(box1._pos_x, box1._top + (box2._bottom - box1._top) / 2)
            inter_2 = Point(box2._pos_x, box1._top + (box2._bottom - box1._top) / 2)
            end = box2.bottom

        elif box1._bottom > box2._top:
            start = box1.bottom
            inter_1 = Point(box1._pos_x, box1._top + (box2._bottom - box1._top) / 2)
            inter_2 = Point(box2._pos_x, box1._top + (box2._bottom - box1._top) / 2)
            end = box2.top

        return Connection([start, inter_1, inter_2, end])
