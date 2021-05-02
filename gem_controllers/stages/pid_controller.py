import numpy as np

from .pi_controller import PIController


class PIDController(PIController):

    @property
    def d_gain(self):
        return self._d_gain

    @d_gain.setter
    def d_gain(self, value):
        self._d_gain = np.array(value)
        self._last_error = np.zeros_like(value)

    def __init__(self):
        super().__init__()
        self._d_gain = np.array([])
        self._last_error = np.array([])

    def __call__(self, state, reference):
        pi_action = super().__call__(state, reference)
        current_error = reference - state[self.state_indices]
        d_action = self._d_gain * (current_error - self._last_error) / self._tau
        self._last_error = current_error
        return pi_action + d_action
