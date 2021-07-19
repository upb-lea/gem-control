import numpy as np
from typing import Tuple

import gem_controllers as gc
from . import ClippingStage


class AbsoluteClippingStage(ClippingStage):

    @property
    def clipping_difference(self) -> np.ndarray:
        return self._clipping_difference

    @property
    def action_range(self) -> Tuple[np.ndarray, np.ndarray]:
        return self._action_range

    def __init__(self, control_task='CC'):
        self._action_range = np.array([]), np.array([])
        self._clipping_difference = np.array([])
        self._control_task = control_task

    def __call__(self, state, reference):
        clipped = np.clip(reference, self._action_range[0], self._action_range[1])
        self._clipping_difference = reference - clipped
        return clipped

    def tune(self, env, env_id, margin=0.0):
        motor_type = gc.utils.get_motor_type(env_id)
        state_names = []
        if self._control_task == 'CC':
            action_names = gc.parameter_reader.voltages[motor_type]
        elif self._control_task == 'TC':
            action_names = gc.parameter_reader.currents[motor_type]
        elif self._control_task == 'SC':
            action_names = ['torque']
        action_indices = [env.state_names.index(action_name) for action_name in action_names]
        limits = env.limits[action_indices] * (1 - margin)
        state_space = env.observation_space[0]
        lower_action_limit = state_space.low[action_indices] * limits
        upper_action_limit = state_space.high[action_indices] * limits
        self._action_range = lower_action_limit, upper_action_limit
        self._clipping_difference = np.zeros_like(lower_action_limit)

    def reset(self):
        self._clipping_difference = np.zeros_like(self._action_range[0])
