import numpy as np

from .stage import Stage


class InputStage(Stage):

    @property
    def state_limits(self):
        return self._state_limits

    @state_limits.setter
    def state_limits(self, value):
        self._state_limits = np.array(value)

    @property
    def reference_limits(self):
        return self._reference_limits

    @reference_limits.setter
    def reference_limits(self, value):
        self._reference_limits = np.array(value)

    def __init__(self):
        super().__init__()
        self._state_limits = np.array([])
        self._reference_limits = np.array([])

    def __call__(self, state, reference):
        # Denormalize State and Reference
        state[:] = state * self._state_limits
        return reference * self._reference_limits

    def tune(self, env, motor_type, action_type, control_task, **__):
        self._state_limits = env.limits
        reference_indices = [env.state_names.index(reference) for reference in env.reference_names]
        self.reference_limits = env.limits[reference_indices]
