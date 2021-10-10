import numpy as np

from .base_controller import BaseController
from .e_base_controller_task import EBaseControllerTask
from ... import parameter_reader as reader
import gem_controllers as gc


class ThreePointController(BaseController):

    @property
    def high_action(self):
        return self._high_action

    @high_action.setter
    def high_action(self, value):
        self._high_action = np.array(value)

    @property
    def low_action(self):
        return self._low_action

    @low_action.setter
    def low_action(self, value):
        self._low_action = np.array(value)

    @property
    def idle_action(self):
        return self._idle_action

    @idle_action.setter
    def idle_action(self, value):
        self._idle_action = np.array(value)

    @property
    def referenced_state_indices(self):
        return self._referenced_state_indices

    @referenced_state_indices.setter
    def referenced_state_indices(self, value):
        self._referenced_state_indices = np.array(value)

    @property
    def hysteresis(self):
        return self._hysteresis

    @hysteresis.setter
    def hysteresis(self, value):
        self._hysteresis = np.array(value)

    @property
    def action_range(self):
        return self._action_range

    @action_range.setter
    def action_range(self, value):
        self._action_range = value

    def __init__(self, control_task):
        super().__init__(control_task)
        self._hysteresis = np.array([])
        self._referenced_state_indices = np.array([])
        self._idle_action = 0.0
        self._high_action = np.array([])
        self._low_action = np.array([])
        self._action_range = (np.array([]), np.array([]))

    def __call__(self, state, reference):
        referenced_states = state[self._referenced_state_indices]
        high_actions = referenced_states + self._hysteresis < reference
        low_actions = referenced_states - self._hysteresis > reference
        return np.select([low_actions, high_actions], [self._low_action, self._high_action], default=self._idle_action)

    def tune(self, env, env_id, **base_controller_kwargs):
        if self._control_task == EBaseControllerTask.SC:
            self._tune_speed_controller(env, env_id)
        elif self._control_task == EBaseControllerTask.CC:
            self._tune_current_controller(env, env_id)
        else:
            raise Exception(f'No tuner available for control_task {self._control_task}.')

    def _tune_current_controller(self, env, env_id):
        motor_type = gc.utils.get_motor_type(env_id)
        voltages = reader.voltages[motor_type]
        currents = reader.currents[motor_type]
        voltage_indices = [env.state_names.index(voltage) for voltage in voltages]
        current_indices = [env.state_names.index(current) for current in currents]
        self.referenced_state_indices = current_indices
        voltage_limits = env.limits[voltage_indices]

        action_range = (
            env.observation_space[0].low[voltage_indices] * voltage_limits,
            env.observation_space[0].high[voltage_indices] * voltage_limits,
        )
        self.action_range = action_range
        # Todo: Calculate Hysteresis based on the dynamics of the underlying control plant
        self.hysteresis = 0.01 * (action_range[1] - action_range[0])
        self.high_action = action_range[1]
        self.low_action = action_range[0]
        self.idle_action = np.zeros_like(action_range[1])

    def _tune_speed_controller(self, env, _env_id):
        torque_index = [env.state_names.index('reference')]
        torque_limit = env.limits[torque_index]
        self.referenced_state_indices = torque_index
        action_range = (
            env.observation_space[0].low[torque_index] * torque_limit,
            env.observation_space[0].high[torque_index] * torque_limit,
        )
        self.action_range = action_range
        # Todo: Calculate Hysteresis based on the dynamics of the underlying control plant
        self.hysteresis = 0.01 * (action_range[1] - action_range[0])
        self.high_action = action_range[1]
        self.low_action = action_range[0]
        self.idle_action = np.zeros_like(action_range[1])
