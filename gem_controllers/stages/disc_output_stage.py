import numpy as np
import gym
from gym_electric_motor.physical_systems import converters as cv

from .stage import Stage
from ..utils import non_parameterized
from ..tuner import parameter_reader as reader


class DiscOutputStage(Stage):

    @property
    def output_stage(self):
        return self._output_stage

    @output_stage.setter
    def output_stage(self, value):
        assert value in [self.to_b6_discrete, self.to_multi_discrete, self.to_discrete]
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
        raise NotImplementedError

    @staticmethod
    def to_multi_discrete(multi_discrete_action):
        return multi_discrete_action

    def to_action(self, state, reference):
        conditions = [reference <= self.low_level, reference >= self.high_level]
        return np.select(conditions, [self.low_action, self.high_action], default=self.idle_action)

    def tune(self, env, motor_type, action_type, control_task):
        voltages = reader.voltages[motor_type]
        voltage_indices = [env.state_names.index(voltage) for voltage in voltages]
        voltage_limits = env.limits[voltage_indices]

        voltage_range = (
            env.observation_space[0].low[voltage_indices] * voltage_limits,
            env.observation_space[0].high[voltage_indices] * voltage_limits,
        )

        self.low_level = -0.33 * (voltage_range[1] - voltage_range[0])
        self.high_level = 0.33 * (voltage_range[1] - voltage_range[0])

        if type(env.action_space) == gym.spaces.MultiDiscrete:
            self.output_stage = DiscOutputStage.to_multi_discrete
        elif type(env.action_space) == gym.spaces.Discrete \
                and type(env.physical_system.converter) != cv.FiniteB6BridgeConverter:
            self.output_stage = DiscOutputStage.to_discrete
        elif type(env.physical_system.converter) == cv.FiniteB6BridgeConverter:
            self.output_stage = DiscOutputStage.to_b6_discrete
        else:
            raise Exception(f'No discrete output stage available for action space {env.action_space}.')
        self.high_action = 1
        if env.action_space.n == 2:  # OneQuadrantConverter
            self.low_action = 0
        else:  # Two and FourQuadrantConverter
            self.low_action = 2
        self.idle_action = 0
