from pylatex import TikZCoordinate


class Point:

    @property
    def coordinate(self):
        return self._coordinate

    @property
    def tikz_coordinate(self):
        return TikZCoordinate(self._coordinate)

    @property
    def x(self):
        return self._coordinate[0]

    @property
    def y(self):
        return self._coordinate[1]

    def __init__(self, x, y):
        self._coordinate = (x, y)

    def __add__(self, other):
        return Point(self.coordinate[0] + other.coordinate[0], self.coordinate[1] + other.coordinate[1])

    def __sub__(self, other):
        return Point(self.coordinate[0] - other.coordinate[0], self.coordinate[1] - other.coordinate[1])

    def __rmul__(self, other):
        return Point(self.coordinate[0] * other, self.coordinate[1] * other)

    def __rdiv__(self, other):
        return Point(self.coordinate[0] / other, self.coordinate[1] / other)

    def __getitem__(self, item):
        return self._coordinate[item]


class Input(Point):
    def __init__(self, x, y):
        super().__init__(x, y)


class Output(Point):
    def __init__(self, x, y):
        super().__init__(x, y)


class Connection:
    def __init__(self, points=[]):
        self.points = points

    def append(self, point):
        self.points.append(point)

    def build(self, pic):
        pass
