import numpy as np
from typing import Tuple

import gem_controllers as gc
from . import ClippingStage


class BoxClippingStage(ClippingStage):

    @property
    def clipping_difference(self) -> np.ndarray:
        return self._clipping_difference

    @property
    def action_range(self) -> Tuple[np.ndarray, np.ndarray]:
        return self._action_range

    def __init__(self):
        self._action_range = np.array([]), np.array([])
        self._clipping_difference = np.array([])

    def __call__(self, state, reference):
        clipped = np.clip(reference, self._action_range[0], self._action_range[1])
        self._clipping_difference = reference - clipped
        return clipped

    def tune(self, env, env_id, state_names=('torque',), margin=0.0):
        state_indices = [env.state_names.index(state_name) for state_name in state_names]
        limits = env.limits[state_indices] * (1 - margin)
        state_space = env.observation_space[0]
        lower_action_limit = state_space.low[state_indices] * limits
        upper_action_limit = state_space.high[state_indices] * limits
        self._action_range = lower_action_limit, upper_action_limit
        self._clipping_difference = np.zeros_like(lower_action_limit)

    def reset(self):
        self._clipping_difference = np.zeros_like(self._action_range[0])
