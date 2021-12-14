from .point import Input, Output, Connection
from .textbox import TextBox


class StageBox:

    @property
    def output(self):
        return self._output

    @property
    def input(self):
        return self._input

    def __init__(self, stage):
        self._stage = stage
        self._text_boxes = []
        self._input = None
        self._output = None
        self._connections = []

    def append(self, obj):
        if isinstance(obj, TextBox):
            self._text_boxes.append(obj)
        elif isinstance(obj, Input):
            self._input = obj
        elif isinstance(obj, Output):
            self._output = obj
        elif isinstance(obj, Connection):
            self._connections.append(obj)

    def build(self, pic):
        for tb in self._text_boxes:
            tb.build(pic)

        for connection in self._connections:
            connection.build(pic)
