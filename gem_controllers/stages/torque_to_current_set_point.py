import numpy as np

from .stage import Stage


class TorqueToCurrentSetPoint(Stage):

    @property
    def conversion_function(self):
        return self._conversion_function

    @conversion_function.setter
    def conversion_function(self, value):
        assert callable(value)
        self._conversion_function = value

    @property
    def action_range(self):
        return self._action_range

    @action_range.setter
    def action_range(self, value):
        self._action_range = tuple(value)

    def __init__(self):
        super().__init__()
        self._conversion_function = lambda state, reference: reference
        self._action_range = (0.0, 1.0)

    def __call__(self, state, reference):
        return np.clip(
            self._conversion_function(state, reference),
            self._action_range[0],
            self._action_range[1]
        )
