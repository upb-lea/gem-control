import numpy as np

from ..base_controllers import BaseController


class IController(BaseController):

    # (float): Additional term to avoid division by zero
    epsilon = 1e-6

    @property
    def i_gain(self):
        return self._i_gain

    @i_gain.setter
    def i_gain(self, value):
        # i_gain is at least zero, to avoid unstable behavior
        value = np.clip(value, 0.0, np.inf)
        self._i_gain = value
        self._integrator_range = (
            self._action_range[0] / (self._i_gain + self.epsilon),
            self._action_range[1] / (self._i_gain + self.epsilon),
        )
        self._i_gain = value

    @property
    def tau(self):
        return self._tau

    @tau.setter
    def tau(self, value: [float, int]):
        self._tau = float(value)

    @property
    def action_range(self):
        return self._action_range

    @action_range.setter
    def action_range(self, value):
        self._action_range = value
        self._integrator_range = (
            self._action_range[0] / (self._i_gain + self.epsilon),
            self._action_range[1] / (self._i_gain + self.epsilon),
        )

    @property
    def state_indices(self):
        return self._state_indices

    @state_indices.setter
    def state_indices(self, value):
        self._state_indices = np.array(value)

    def __init__(self, control_task):
        super().__init__(control_task)
        self._state_indices = np.array([])
        self._action_range = (np.array([]), np.array([]))
        self.i_gain = np.array([])
        self._integrator = np.array([])
        self._tau = None

    def __call__(self, state, reference):
        return self.control(state, reference)

    def _control(self, _state, _reference):
        return self._i_gain * self._integrator

    def _clip(self, action):
        return np.clip(action, self._action_range[0], self._action_range[1])

    def control(self, state, reference):
        action = self._control(state, reference)
        self.integrate(state, reference)
        return self._clip(action)

    def integrate(self, state, reference):
        error = reference - state
        self._integrator = self._integrator + error * self._tau
        self._integrator = np.clip(self._integrator, self._integrator_range[0], self._integrator_range[1])

    def reset(self):
        super().reset()
        self._integrator = np.zeros_like(self._i_gain)
