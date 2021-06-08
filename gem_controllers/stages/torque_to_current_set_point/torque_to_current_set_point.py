import numpy as np

import gem_controllers as gc
from gem_controllers.stages.stage import Stage
from gem_controllers.tuner import parameter_reader as reader


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

    def tune(self, env, env_id, current_safety_margin=0.2):
        motor_type = gc.utils.get_motor_type(env_id)
        currents = reader.currents[motor_type]
        current_indices = [env.state_names.index(current) for current in currents]
        state_space = env.observation_space[0]
        upper_limit = env.limits[current_indices] * state_space.high[current_indices] * (1 - current_safety_margin)
        lower_limit = env.limits[current_indices] * state_space.low[current_indices] * (1 - current_safety_margin)
        self.action_range = (lower_limit, upper_limit)
