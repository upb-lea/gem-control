from pylatex import TikZCoordinate


class Point:

    @property
    def coordinate(self):
        return self._coordinate

    @property
    def tikz(self):
        return TikZCoordinate(self.x, self.y)

    @property
    def x(self):
        return self._coordinate[0]

    @property
    def y(self):
        return self._coordinate[1]

    @property
    def input(self):
        return Input(x=self.x, y=self.y)

    @property
    def output(self):
        return Output(x=self.x, y=self.y)

    @property
    def direction(self):
        return self._direction

    def __init__(self, x: float, y: float, direction: str = None):
        self._coordinate = (x, y)
        self._direction = direction if direction in ['north', 'west', 'south', 'east'] else False

    def __add__(self, other):
        if isinstance(other, list):
            return [self] + other

        return Point(self.coordinate[0] + other.coordinate[0], self.coordinate[1] + other.coordinate[1])

    def __sub__(self, other):
        return Point(self.coordinate[0] - other.coordinate[0], self.coordinate[1] - other.coordinate[1])

    def __mul__(self, other):
        return Point(self.coordinate[0] * other, self.coordinate[1] * other)

    def __truediv__(self, other):
        return Point(self.coordinate[0] / other, self.coordinate[1] / other)

    def __getitem__(self, item):
        return self._coordinate[item]

    def __repr__(self):
        return f'Point({self.x}, {self.y})'

    def add(self, x: float, y: float):
        return Point(self.x + x, self.y + y)

    def add_x(self, val: float):
        return Point(self.x + val, self.y)

    def add_y(self, val: float):
        return Point(self.x, self.y + val)

    @staticmethod
    def get_mid(p1, p2):
        return Point((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)

class Input(Point):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)


class Output(Point):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
