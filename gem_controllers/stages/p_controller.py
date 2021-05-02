import numpy as np

from .stage import Stage


class PController(Stage):

    @property
    def p_gain(self):
        return self._p_gain

    @p_gain.setter
    def p_gain(self, value):
        self._p_gain = value

    @property
    def state_indices(self):
        return self._state_indices

    @state_indices.setter
    def state_indices(self, value):
        self._state_indices = np.array(value)

    def __call__(self, state, reference):
        return self.control(state, reference)

    def __init__(self, p_gain=np.array([0.0]), action_range=(np.array([0.0]), np.array([0.0]))):
        super().__init__()
        self._p_gain = p_gain
        self._action_range = action_range
        self._state_indices = np.array([])

    def _control(self, state, reference):
        return self._p_gain * (reference - state)

    def _clip(self, action):
        return np.clip(action, self._action_range[0], self._action_range[1])

    def control(self, state, reference):
        return self._clip(self._control(state[self._state_indices], reference))

    def tune(self, env, motor_type, action_type, control_task, sub_control_task='CC'):
        pass

