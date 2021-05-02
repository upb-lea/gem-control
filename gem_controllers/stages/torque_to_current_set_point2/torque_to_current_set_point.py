import numpy as np

from gem_controllers.stages.stage import Stage


class TorqueToCurrentSetPoint(Stage):

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
            self._torque_to_current(state, reference),
            self._action_range[0],
            self._action_range[1]
        )

    def _torque_to_current(self, state, reference):
        raise NotImplementedError
