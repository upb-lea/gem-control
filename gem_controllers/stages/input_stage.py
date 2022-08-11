import numpy as np

from .stage import Stage


class InputStage(Stage):
    """This class denormalizes the state and reference."""

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
        """Denormalize state and reference"""
        state[:] = state * self._state_limits
        return reference * self._reference_limits

    def tune(self, env, env_id, **__):
        """Set the limits of the state and the reference"""
        self._state_limits = env.limits
        reference_indices = [env.state_names.index(reference) for reference in env.reference_names]
        self.reference_limits = env.limits[reference_indices]
