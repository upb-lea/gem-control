from pylatex import (Document, TikZ, TikZNode,
                     TikZDraw, TikZCoordinate,
                     TikZUserPath, TikZOptions,
                     Command, PageStyle)

from .point import Point, Input, Output, Connection
from .textbox import TextBox


class StageBox:

    def __init__(self):
        self._text_boxes = []
        self._inputs = []
        self._outputs = []
        self._connections = []

    def append(self, obj):
        if isinstance(obj, TextBox):
            self._text_boxes.append(obj)
        elif isinstance(obj, Input):
            self._inputs.append(obj)
        elif isinstance(obj, Output):
            self._outputs.append(obj)
        elif isinstance(obj, Connection):
            self._connections.append(obj)

    def build(self, pic):
        for tb in self._text_boxes:
            tb.build(pic)

        for connection in self._connections:
            connection.build(pic)
