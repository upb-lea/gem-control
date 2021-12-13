from pylatex import (Document, TikZ, TikZNode,
                     TikZDraw, TikZCoordinate,
                     TikZUserPath, TikZOptions,
                     Command, PageStyle)


class TextBox:

    @property
    def right(self):
        return TikZCoordinate(self._right, self._pos_y)

    @property
    def left(self):
        return TikZCoordinate(self._left, self._pos_y)

    @property
    def top(self):
        return TikZCoordinate(self._pos_x, self._top)

    @property
    def bottom(self):
        return TikZCoordinate(self._pos_x, self._bottom)

    def __init__(self, position, size, text, fill, draw):
        self._pos_x = position.x
        self._pos_y = position.y
        (self._size_x, self._size_y) = size
        self._text = text
        self._fill = fill
        self._draw = draw

        self._right = self._pos_x + self._size_x / 2
        self._left = self._pos_x - self._size_x / 2
        self._top = self._pos_y + self._size_y / 2
        self._bottom = self._pos_y - self._size_y / 2

        self._len_text = len(self._text)

        self._node_kwargs = {'align': 'center',
                            'text width': str(self._size_x) + 'cm'}

        self._text_pos = [TikZCoordinate(self._pos_x, self._top - (i + 1) / (self._len_text + 1) * self._size_y) for i in
                          range(self._len_text)]

    def build(self, pic):
        box = TikZDraw([TikZCoordinate(self._left, self._top), 'rectangle', TikZCoordinate(self._right, self._bottom)],
                       TikZOptions(draw=self._draw, fill=self._fill))
        pic.append(box)

        for text, pos in zip(self._text, self._text_pos):
            pic.append(TikZNode(
                text=text,
                at=pos,
                handle='box',
                options=TikZOptions(self._node_kwargs)
            )
        )

    @staticmethod
    def connect(pic, box1, box2):

        if box1._right < box2._left:
            start = box1.right
            inter_1 = TikZCoordinate(box1._right + (box2._left - box1._right) / 2, box1._pos_y)
            inter_2 = TikZCoordinate(box1._right + (box2._left - box1._right) / 2, box2._pos_y)
            end = box2.left

        elif box1._left > box2._right:
            start = box1.left
            inter_1 = TikZCoordinate(box1._right + (box2._left - box1._right) / 2, box1._pos_y)
            inter_2 = TikZCoordinate(box1._right + (box2._left - box1._right) / 2, box2._pos_y)
            end = box2.right

        elif box1._top < box2._bottom:
            start = box1.top
            inter_1 = TikZCoordinate(box1._pos_x, box1._top + (box2._bottom - box1._top) / 2)
            inter_2 = TikZCoordinate(box2._pos_x, box1._top + (box2._bottom - box1._top) / 2)
            end = box2.bottom

        elif box1._bottom > box2._top:
            start = box1.bottom
            inter_1 = TikZCoordinate(box1._pos_x, box1._top + (box2._bottom - box1._top) / 2)
            inter_2 = TikZCoordinate(box2._pos_x, box1._top + (box2._bottom - box1._top) / 2)
            end = box2.top

        else:
            return

        with pic.create(TikZDraw()) as path:
            path.append(start)
            path.append(TikZUserPath('edge', TikZOptions()))
            path.append(inter_1)

            path.append(inter_1)
            path.append(TikZUserPath('edge', TikZOptions()))
            path.append(inter_2)

            path.append(inter_2)
            path.append(TikZUserPath('edge', TikZOptions('-latex')))
            path.append(end)