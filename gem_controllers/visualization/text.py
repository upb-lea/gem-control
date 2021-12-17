from pylatex import TikZNode, TikZCoordinate, TikZOptions
from .point import Point


class Text:

    def __init__(self, text: list, position: Point = Point(0, 0), size: tuple = (2, 2)):
        self._text = text if isinstance(text, list) else tuple(str(text))
        self._len_text = len(self._text)
        self._position = position
        self._text_position = []
        self._size = size
        self._options = None

    def define(self, **kwargs):
        self._position = kwargs.get('position')
        self._size = kwargs.get('size')
        self._options = {'align': 'center', 'text width': str(self._size[0]) + 'cm'}
        top = self._position[1] + self._size[1] / 2
        self._text_position = [TikZCoordinate(self._position.x, top - (i + 1) / (self._len_text + 1) * self._size[1])
                               for i in range(self._len_text)]

    def build(self, pic):
        for text, pos in zip(self._text, self._text_position):
            pic.append(TikZNode(text=text, at=pos, handle='box', options=TikZOptions(self._options)))