from pylatex import (Document, TikZ, TikZNode,
                     TikZDraw, TikZCoordinate,
                     TikZUserPath, TikZOptions,
                     Command, PageStyle)


from .textbox import TextBox


class StageBox:
    def __init__(self):
        self.boxes = []
        self.inputs = []
        self.outputs = []

    def append(self, obj):
        if isinstance(obj, TextBox):
            self.boxes.append(obj)
        elif isinstance(obj, Input):
            self.inputs.append(obj)
        elif isinstance(obj, Output):
            self.outputs.append(obj)

    def build(self, pic):
        for box in self.boxes:
            pic.append(box)


class Point:
    def __init__(self, coordinate):
        self.coordinate = TikZCoordinate(coordinate)


class Input(Point):
    def __init__(self, coordinate):
        super().__init__(coordinate)


class Output(Point):
    def __init__(self, coordinate):
        super().__init__(coordinate)
