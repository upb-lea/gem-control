import numpy as np
import gym
from gym_electric_motor.physical_systems import converters as cv

from .stage import Stage
from ..utils import non_parameterized
from .. import parameter_reader as reader
import gem_controllers as gc


class DiscOutputStage(Stage):

    @property
    def output_stage(self):
        return self._output_stage

    @output_stage.setter
    def output_stage(self, value):
        assert value in [self.to_b6_discrete, self.to_multi_discrete, self.to_discrete, self.to_finite_multi]
        self._output_stage = value

    def __init__(self):
        super().__init__()
        self.high_level = 0.0
        self.low_level = 0.0
        self.high_action = 0
        self.low_action = 0
        self.idle_action = 0
        self._output_stage = non_parameterized

    def __call__(self, state, reference):
        return self._output_stage(self.to_action(state, reference))

    @staticmethod
    def to_discrete(multi_discrete_action):
        return multi_discrete_action[0]

    @staticmethod
    def to_b6_discrete(multi_discrete_action):
        return np.sum([a * 2 ** n for n, a in enumerate(multi_discrete_action[::-1])])

    @staticmethod
    def to_multi_discrete(multi_discrete_action):
        return multi_discrete_action

    @staticmethod
    def to_finite_multi(multi_discrete_action):
        return np.array([DiscOutputStage.to_b6_discrete(multi_discrete_action[:3]), multi_discrete_action[3]])

    def to_action(self, _state, reference):
        conditions = [reference <= self.low_level, reference >= self.high_level]
        return np.select(conditions, [self.low_action, self.high_action], default=self.idle_action)

    def tune(self, env, env_id, **__):
        action_type, _, motor_type = gc.utils.split_env_id(env_id)
        voltages = reader.get_output_voltages(motor_type, action_type)
        voltage_indices = [env.state_names.index(voltage) for voltage in voltages]
        voltage_limits = env.limits[voltage_indices]

        voltage_range = (
            env.observation_space[0].low[voltage_indices] * voltage_limits,
            env.observation_space[0].high[voltage_indices] * voltage_limits,
        )

        self.low_level = -0.33 * (voltage_range[1] - voltage_range[0])
        self.high_level = 0.33 * (voltage_range[1] - voltage_range[0])

        if type(env.action_space) == gym.spaces.MultiDiscrete \
                and type(env.physical_system.converter) != cv.FiniteMultiConverter:
            self.output_stage = DiscOutputStage.to_multi_discrete
            self.low_action = []
            self.idle_action = []
            self.high_action = []
            for n in env.action_space.nvec:
                low_action, idle_action, high_action = self._get_actions(n)
                self.low_action.append(low_action)
                self.idle_action.append(idle_action)
                self.high_action.append(high_action)

        elif type(env.action_space) == gym.spaces.Discrete \
                and type(env.physical_system.converter) != cv.FiniteB6BridgeConverter:
            self.output_stage = DiscOutputStage.to_discrete
            self.low_action, self.idle_action, self.high_action = self._get_actions(env.action_space.n)
        elif type(env.physical_system.converter) == cv.FiniteB6BridgeConverter:
            self.output_stage = DiscOutputStage.to_b6_discrete
            self.low_level = self.high_level = 0
            self.low_action = 0
            self.high_action = 1
        elif type(env.physical_system.converter) == cv.FiniteMultiConverter:
            self.output_stage = DiscOutputStage.to_finite_multi
            self.low_action = [0, 0, 0, 2]
            self.high_action = [1, 1, 1, 1]
            self.idle_action = [0, 0, 0, 0]

        else:
            raise Exception(f'No discrete output stage available for action space {env.action_space}.')

    @staticmethod
    def _get_actions(n):
        high_action = 1
        if n == 2:  # OneQuadrantConverter
            low_action = 0
        else:  # Two and FourQuadrantConverter
            low_action = 2
        idle_action = 0
        return low_action, idle_action, high_action
