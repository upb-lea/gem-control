import numpy as np

import gem_controllers as gc


class SquaredClippingStage(gc.stages.clipping_stages.ClippingStage):

    @property
    def clipping_difference(self) -> np.ndarray:
        return self._clipping_difference

    @property
    def limits(self):
        return self._limits

    @property
    def margin(self):
        return self._margin

    def __init__(self):
        self._clipping_difference = np.array([])
        self._margin = 1.0
        self._limits = np.array([])

    def __call__(self, state, reference):
        relative_reference_length = np.sum((reference/self._limits)**2)
        relative_maximum = 1 - self._margin
        clipped = reference \
            if relative_reference_length < relative_maximum**2 \
            else reference / relative_reference_length * relative_maximum
        self._clipping_difference = reference - clipped
        return clipped

    def tune(self, env, env_id, state_names=('torque',), margin=0.0):
        state_indices = [env.state_names.index(state_name) for state_name in state_names]
        self._limits = env.limits[state_indices]

    def reset(self):
        self._clipping_difference = np.zeros_like(self._limits)
