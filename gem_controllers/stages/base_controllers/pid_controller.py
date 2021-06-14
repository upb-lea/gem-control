import numpy as np

from .pi_controller import PIController


class PIDController(PIController):

    @property
    def d_gain(self):
        return self._d_gain

    @d_gain.setter
    def d_gain(self, value):
        self._d_gain = np.array(value)
        self._last_error = np.zeros_like(self._d_gain, dtype=float)

    def __init__(self, control_task):
        super().__init__(control_task)
        self._d_gain = np.array([])
        self._last_error = np.array([])

    def control(self, state, reference):
        pi_action = super().control(state, reference)
        current_error = reference - state[self.state_indices]
        d_action = self._d_gain * (current_error - self._last_error) / self._tau
        self._last_error = current_error
        return pi_action + d_action

    def _tune_current_controller(self, env, env_id, a=4):
        super()._tune_current_controller(env, env, env_id, a)
        self.d_gain = self.p_gain * self.tau

    def _tune_speed_controller(self, env, env_id, a=4, t_n=None):
        super()._tune_speed_controller(env, env_id, a)
        self.d_gain = self.p_gain * self.tau

