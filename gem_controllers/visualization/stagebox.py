from .point import Input, Output
from .textbox import TextBox
from .connection import Connection
from .circle import Circle


class StageBox:

    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, out):
        if isinstance(out, Output):
            self._output = out

    @property
    def input(self):
        return self._input

    @input.setter
    def input(self, inp):
        if isinstance(inp, Input):
            self._input = Input

    def __init__(self, stage, input: Input = None, output: Output = None):
        self._stage = stage
        self._text_boxes = []
        self._circles = []
        self._input = input
        self._output = output
        self._connections = []

    def __repr__(self):
        return f'StageBox: {self._stage} Controller'

    def append(self, obj):
        if isinstance(obj, TextBox):
            self._text_boxes.append(obj)
        elif isinstance(obj, Connection):
            self._connections.append(obj)
        elif isinstance(obj, Circle):
            self._circles.append(obj)

    def build(self, pic):
        for text_box in self._text_boxes:
            text_box.build(pic)

        for circle in self._circles:
            circle.build(pic)

        for connection in self._connections:
            connection.build(pic)
