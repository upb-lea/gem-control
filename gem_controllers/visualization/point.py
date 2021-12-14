from pylatex import TikZCoordinate, TikZDraw, TikZUserPath, TikZOptions


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

    def __init__(self, x, y, direction=None):
        self._coordinate = (x, y)
        self._direction = direction if direction in ['north', 'west', 'south', 'east'] else None

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
    @property
    def tikz(self):
        return [point.tikz for point in self._points]

    def __init__(self, points):
        self._points = points

    def append(self, point):
        if isinstance(point, Point):
            self._points.append(point)

    def build(self, pic):
        with pic.create(TikZDraw()) as path:
            path.append(self._points[0].tikz)
            for point in self.tikz[1:-1]:
                path.append(TikZUserPath('edge', TikZOptions()))
                path.append(point)
                path.append(point)
            path.append(TikZUserPath('edge', TikZOptions('-latex')))
            path.append(self._points[-1].tikz)
